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

def download_file_with_retry(url, file_name):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 30))  # Default to 30 seconds if header is missing
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return download_file_with_retry(url, file_name)  # Recursively retry downloading the file
        else:
            raise
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)




def get_files_from_url(url, pattern):
    """Download all files matching the given regex pattern from the URL."""
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

    return matching_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The URL to download files from.")
    parser.add_argument("pattern", help="The regex pattern to match file names.")
    args = parser.parse_args()

    pattern = re.compile(args.pattern, re.IGNORECASE)  # Compile pattern here for clarity

    matching_files = get_files_from_url(args.url, pattern)
    if matching_files:
        print("Downloaded files:")
        for filename in matching_files:
            print(filename)
    else:
        print("No matching files found or download failed.")
https://www.eacc.ie/
