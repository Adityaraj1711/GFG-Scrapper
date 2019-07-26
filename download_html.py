#!/usr/bin/env python3
"""
Download HTML pages from Geeks for Geeks and clean them.

Usage: download_html [options] <json>

Options:

    -f --force       Overwrite destination
"""


import os
import json

from collections import OrderedDict

import requests
import requests_cache

from docopt import docopt

import glean

ROOT = "Topics"
ROOT_HTML = "HTML"


requests_cache.install_cache("geeks")


def mkdir(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)


def download(urls, folder, force=False):
    mkdir(folder)

    cleaned_html = []

    for title, url in urls.items():

        file = os.path.join(folder,
                            url.split('/')[-2] + ".html")

        if not force and os.path.isfile(file):
            print(file)
            with open(file) as inp:
                cleaned = inp.read()
        else:
            print(url, file)

            r = requests.get(url)
            cleaned = glean.clean(r.content, title)

            # Write content to individual files
            with open(file, 'w') as out:
                out.write(cleaned)

        cleaned_html.append(cleaned)

    # Write all content to a single file as well
    mkdir(ROOT_HTML)
    cleaned_file = os.path.join(
        ROOT_HTML,
        folder.split('/')[-1] + ".html"
    )

    with open(cleaned_file, 'w') as out:
        out.write("\n".join(cleaned_html))


if __name__ == '__main__':

    args = docopt(__doc__)

    fpath = args['<json>']
    fname = os.path.split(fpath)[1]
    topic = os.path.splitext(fname)[0]

    with open(fpath) as inp:
        input_json = json.load(inp, object_pairs_hook=OrderedDict)

    download(
        urls=input_json,
        folder=os.path.join(ROOT, topic),
        force=args["--force"],
    )
