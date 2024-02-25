import re
import requests
from bs4 import BeautifulSoup
import argparse
import os
from urllib.parse import urljoin  # Import urljoin for creating absolute urls
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Func to ensure all url begin with http:// or https://
def prepend_http(url_or_urls):
    if isinstance(url_or_urls, list):
        return ["http://" + url if not url.startswith(("http://", "https://")) else url for url in url_or_urls]
    else:
        return "http://" + url_or_urls if not url_or_urls.startswith(("http://", "https://")) else url_or_urls



def download_file_with_retry(url, file_name, output_dir):
    """Downloads files with retry logic and handles output directory."""
    try:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Construct the full file path using os.path.join
        full_file_path = os.path.join(output_dir, file_name)

        with open(full_file_path, "wb") as f:
            print(f"Writing to: {full_file_path}")
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 30))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            if args.wait != 0:
                time.sleep(args.wait)
            else:
                time.sleep(retry_after)
            return download_file_with_retry(
                url, file_name, output_dir
            )  # Recursively retry
        else:
            raise

    except FileNotFoundError:
        print(f"Failed to create output directory: {output_dir}")


def get_files_from_url(url, pattern, output_dir):
    """Checks the source HTML, downloads matching files, and handles output directory."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        matching_files = []

        for link in links:
            if re.search(pattern, link):
                absolute_url = urljoin(url, link)
                file_name = os.path.basename(link)
                download_file_with_retry(absolute_url, file_name, output_dir)
                matching_files.append(file_name)

        return matching_files

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []


# Function for implementing advanced regex matching, allowing users to use logical operands such as AND/OR/NOT/XOR/XNOR
def tokenize(expression):
    # Regular expression for matching tokens: regex patterns, logical operators, and parentheses
    token_pattern = re.compile(
        r'("(?:\\.|[^"\\])*")'  # Match quoted strings (regex patterns)
        r"|(AND|OR|NOT)"  # Match logical operators
        r"|(\(|\))",  # Match parentheses
        re.IGNORECASE,
    )

    tokens = []
    for match in token_pattern.finditer(expression):
        # Extract matched groups, ignoring None values
        token = next(filter(None, match.groups()))
        tokens.append(token)
    return tokens


# Main logic
if __name__ == "__main__":
    # Define arguments
    parser = argparse.ArgumentParser(
        prog="DoRePy",
        description="Python program for downloading links from a url matching a regex pattern",
        epilog='USAGE: dorepy [-b or --batch] "url" "REGEX" -o "DOWNLOAD_DIRECTORY"',
    )
    parser.add_argument(
        "-b",
        "--batch",
        action="store",
        help='Provide multiple url enclosed in quotes (e.g `-b "example1.com example2.com"`). Separate url with spaces.',
    )
    parser.add_argument(
        "url", nargs="?", help="One url (required if not using --batch)"
    )
    parser.add_argument(
        "REGEX",
        nargs="?",
        default=".*",
        help="Regex pattern (defaults to .* to match all linked files)",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs=1,
        help="Output directory"
    )
    parser.add_argument(
        "-c",
        "--caps-sensitive",
        action="store_true",
        help="Make regex capitalisation-sensitive, by default regex-matching is caps insensitive",
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        default=0,
        help="Seconds to wait between downloads (defaults to 0)",
    )
    parser.add_argument(
        "-a",
        "--advanced-regex",
        action="store_true",
        help='NOT YET IMPLEMENTED: Allow multiple regex patterns with logical operations, e.g. `(("dogs" NOT "cats") AND "pet" AND "\.html$")`',
    )

    args = parser.parse_args()

    # Correctly process and apply prepend_http
    if args.batch:
        urls = args.batch.split()  # Split the batch input into a list of URLs
    else:
        urls = [args.url]  # Wrap the single URL in a list for consistent handling

    urls = prepend_http(urls)  # Apply prepend_http to either single or batch URLs
    # Split batch URLs into a list if present

    output_dir = args.output[0] if args.output else os.getcwd()  # Correctly accessing the output directory

    # Iterate over each URL in the urls list
    for url in urls:    
        if url:  # Ensure url is not None or empty
            if args.caps_sensitive:
                pattern = re.compile(args.REGEX)
            else:
                pattern = re.compile(args.REGEX, re.IGNORECASE)  # Incorrect flag usage for case-sensitive

            matching_files = get_files_from_url(url, pattern, output_dir)
            if matching_files:
                print("Downloaded files:")
                for filename in matching_files:
                    print(filename)
            else:
                print("No matching files found or download failed.")