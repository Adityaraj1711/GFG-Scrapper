#! /usr/bin/env python3
"""
Create monolithic document from multilevel JSON using download_html.py

Usage: download_total [options] <json>

Options:

    -f --force       Overwrite destination
"""

from bs4 import BeautifulSoup
from docopt import docopt
import json
from collections import OrderedDict
import os.path

import download_html

ROOT_JSON = "TOTAL_JSON"
ROOT_FINAL_HTML = download_html.ROOT_HTML  # original HTML root

def folder_html(folder):
    return folder.split('/')[-1] + ".html"


HEADS = 6  # number of possible headers in html
def subtract_header(html_content, n):
    soup = BeautifulSoup(html_content, "lxml")
    for b in soup.find_all(["html", "body"]):
        b.name = "div"
    for i in range(HEADS - n, 0, -1):
        for match in soup.find_all("h%d" % i):
            pass
            match.name = "h%d" % (i + n)
    return soup.prettify(formatter="html")


def _download_all(urls, folder, force=False, document="", level=1):
    if not len(urls):
        return ""
    achild = next(iter(urls.values()))
    files = []
    if isinstance(achild, OrderedDict):
        # If any child is dictionary all should
        for key, urlgroup in urls.items():
            if len(key) > 0:
                header = "<h%d>%s</h%d>\n" % (level, key, level)
                newlevel = level + 1
            else:
                header = ""
                newlevel = level
            newfolder = os.path.join(folder, key)
            document += header + _download_all(urlgroup, os.path.join(folder, key), force, document, newlevel)

        return document
    else:
        # This level is ready to go to download_html
        download_html.download(urls, folder, force)
        html_src = os.path.join(download_html.ROOT_HTML, folder_html(folder))
        return subtract_header(open(html_src, "r").read(), level-1)


def download_all(urls, folder, force=False):
    title = ""
    if len(urls) == 1:
        head, urls = next(iter(urls.items()))
        title = "<title>" + head + "</title>"
    return "<html><head>" + title + "</head><body>\n" + _download_all(urls, folder, force) + "\n</body></html>"


def main():
    args = docopt(__doc__)

    fpath = args['<json>']
    fname = os.path.split(fpath)[1]
    topic = os.path.splitext(fname)[0]

    with open(fpath) as inp:
        input_json = json.load(inp, object_pairs_hook=OrderedDict)

    doc = download_all(
        urls=input_json,
        folder=download_html.ROOT,
        force=args["--force"]
    )

    total_html = os.path.join(ROOT_FINAL_HTML, topic) + ".html"
    with open(total_html, "w+") as outfile:
        outfile.write(doc)

if __name__ == "__main__":
  main()
