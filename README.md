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

Below are the two methods of installing **DoRePy**
1. Pip

```bash
pip install DoRePy
```

2. Clone the repo
Clone this repository or simply download `dorepy.py` to your local machine:

```bash
git clone https://github.com/CillySu/DoRePy/dorepy.git
```

### Usage
Navigate to the directory in which you want to have the files downloaded

```bash
dorepy [URL] [PATTERN]
```

if you installed with pip. If you downloaded the .py run the dorepy.py file instead such as `python ./dorepy.py [URL] [PATTERN]`
Where:

[URL] is the webpage URL from which you want to download files.
[PATTERN] is the regex pattern that matches the file names you want to download.

Example:

```bash
python dorepy.py "http://example.com" "\.pdf$"
```

This command downloads all PDF files which are linked to on http://example.com.

1. `\.` matches all literal `.`
2. `pdf` matches pdf (when following a literal `.`)
3. `$` matches the end of the filename, the end result being that files *ending* in `.pdf` are matched. See [RegExr](https://regexr.com) for help on building regex patterns.

### Roadmap

The following features are envisaged for **DoRePy**'s second movement:

1. Batch URL support, allowing one regex pattern to be matched against a list of URLs
2. Combinatorial regex logic matching, such that users can supply multiple regex patterns and combine them with logical operands AND/NOT/NOR/XOR/XNOR
3. User-specified output directory for downloading instead of using the present working directory
4. User-specified sleep time instead of the current behaviour (check for website-defined retry-after time, failing this default to 30s)
5. Recursive downloading of links which are present in pages linked to in a URL, with CLI arguments to define depth of recursion such as -L in `tree`
6. Ability to control whether regex is cAsE sEnSiTiVe (currently always case insensitive)
   
##### Contributing
Feel like DoRePy hit the wrong note? Are we singing off a different hymn sheet? Fork the repo, perform your cover version, and submit a pull request. 

##### License
Distributed under the **MIT** License. See LICENSE for more information.

##### A Note on Responsible Use
Please use DoRePy wisely and respect website terms of service and your local laws as applicable.
