# DoRePy - (Do)wnload (Re)gex (Py)thon

**DoRePy** (pronounced like *doe-ray-pee*) is your go-to script for automating the download of files from a webpage that match a specific regex pattern. Fed up with manually sifting through pages to download files? DoRePy has got your back!

## Features

- **Regex Pattern Matching**: Use the power of regular expressions to target exactly the files you need.
- **Retry Logic**: Network hiccup? No problem. DoRePy retries failed downloads, respecting rate limits like a well-mannered netizen.

## Getting Started

### Prerequisites

- Python 3
- Requests: `pip install requests`
- BeautifulSoup: `pip install beautifulsoup4`

### Installation

Clone this repository or simply download `dorepy.py` to your local machine:

```bash
git clone https://github.com/CillySu/DoRePy/dorepy.git
```

### Usage
Navigate to the directory containing dorepy.py and run:

```bash
python dorepy.py [URL] [PATTERN]
```

Where:

[URL] is the webpage URL from which you want to download files.
[PATTERN] is the regex pattern that matches the file names you want to download.

Example:

```bash
python dorepy.py "http://example.com" "\.pdf$"
```

This command downloads all PDF files which are linked to on http://example.com.

##### Contributing
Feel like DoRePy missed a beat? Fork the repo, add your spin, and submit a pull request. All contributions are welcome!

##### License
Distributed under the **MIT** License. See LICENSE for more information.

##### A Note on Responsible Use
Please use DoRePy wisely and respect website terms of service and your local laws as applicable.
