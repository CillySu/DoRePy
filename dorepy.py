import re
import requests
from bs4 import BeautifulSoup
import argparse
import os
from urllib.parse import urljoin  # Import urljoin for creating absolute URLs
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Func to ensure all URLs begin with http:// or https://
def prepend_http(url):
    """Ensure each URL is prepended with http:// if not already specified."""
    for i, url in enumerate(url):
        if not re.match(r'http[s]?://', url):
            url[i] = 'http://' + url
    return url

# Checks regex is valid and throws an error if it is not
def validate_regex(pattern):
    try:
        re.compile(pattern)
        return pattern
    except re.error:
        raise argparse.ArgumentTypeError(f"'{pattern}' is not a valid regex")

# Logic for file downloads, unused func for now, using download_file_with_retry()
def download_file(url, file_name):
    session = requests.Session()
    # Define a retry strategy
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    with session.get(url, stream=True, timeout=10) as r:
        r.raise_for_status()  # Raises an HTTPError if the response was an error
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

# Downloads files and tries to navigate around rate-limits.
def download_file_with_retry(url, file_name):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 30))  # Default to 30 seconds if header is missing
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            if args.wait != 0:
                time.sleep(args.wait)
            else:
                time.sleep(retry_after)
            return download_file_with_retry(url, file_name)  # Recursively retry downloading the file
        else:
            raise
    # If the user has provided a directory with -o or --output, we prepend this to the filename to be downloaded before writing chunks to it
    if args.output is not None:
        file_name = f"{args.output}/{file_name}"
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# Checks the source HTML of the URL given in args.url or args.batch and downloads the files which match args.REGEX
def get_files_from_url(url, pattern):
    # Attempt to get the source code from the URL specified
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP request errors
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    matching_files = []

    for link in links:
        if re.search(pattern, link):
            # Create an absolute URL by combining the base URL with the relative link
            absolute_url = urljoin(url, link)
            file_name = os.path.basename(link)
            try:
                download_file_with_retry(absolute_url, file_name)
                matching_files.append(file_name)
            except requests.RequestException as e:
                print(f"Failed to download {absolute_url}: {e}")
    # Prints the linked files which are to be downloaded
    return matching_files

# Function for implementing advanced regex matching, allowing users to use logical operands such as AND/OR/NOT/XOR/XNOR
def tokenize(expression):
    # Regular expression for matching tokens: regex patterns, logical operators, and parentheses
    token_pattern = re.compile(
        r'("(?:\\.|[^"\\])*")'  # Match quoted strings (regex patterns)
        r'|(AND|OR|NOT)'  # Match logical operators
        r'|(\(|\))'  # Match parentheses
        , re.IGNORECASE)

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
        prog='DoRePy',
        description='Python program for downloading links from a URL matching a regex pattern',
        epilog='USAGE: dorepy [-b or --batch] "URL" "REGEX" -o "DOWNLOAD_DIRECTORY'
    )
    parser.add_argument('-b', '--batch', action='store', help='Provide multiple URLs enclosed in quotes (e.g `-b "example1.com example2.com"`). Separate URLs with spaces.')
    parser.add_argument('URL', nargs='?', help='One URL (required if not using --batch)')
    parser.add_argument('REGEX', nargs='?', default='.*', help='Regex pattern (defaults to .* to match all linked files)')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-c', '--caps-sensitive', action='store_true', help='Make regex capitalisation-sensitive, by default regex-matching is caps insensitive')
    parser.add_argument('-w', '--wait', type=int, default=0, help='Seconds to wait between downloads (defaults to 0)')
    parser.add_argument('-a', '--advanced-regex', help='NOT YET IMPLEMENTED: Allow multiple regex patterns with logical operations, e.g. `(("dogs" NOT "cats") AND "pet" AND "\.html$")`')


    args = parser.parse_args()
    if args.batch:
        url = prepend_http(args.batch)
    else:
        url = prepend_http(args.URL)

    if args.caps_sensitive:
        pattern = re.compile(args.pattern, re.IGNORECASE)  # Compile pattern and set case-sensitivity to false
    else:
        pattern = re.compile(args.pattern)  # Compile pattern with case sensitivity

    if args.REGEX is not None:
        validate_regex(args.REGEX)
    else:
        print("No regex provided, assuming all linked files are to be downloaded. Setting regex pattern = `.*`")

    matching_files = get_files_from_url(args.url, pattern)
    if matching_files:
        print("Downloaded files:")
        for filename in matching_files:
            print(filename)
    else:
        print("No matching files found or download failed.")

    