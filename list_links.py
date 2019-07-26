#!/usr/bin/env python3.6

"""
List all links on all pages of a geeks for geeks tag.

By default, a JSON is generated, which can be edited by hand.

Usage: list_links [options] <URL>
"""

import os
import sys
import json

from collections import OrderedDict

import requests
import pyquery

from bs4 import BeautifulSoup

ROOT_JSON = "JSON/"

URL = sys.argv[1].rstrip('/')
TAG = URL.split('/')[-1].title()

FNAME = ROOT_JSON + f"{TAG}.json"


def abort(msg):
    print(msg, file=sys.stderr)
    exit(1)


def print_titles(content):
    for title in content.find_all('strong'):
        print(title.text.strip())


def fetch_post_links(urls, filename=None, combined=False):
    if type(urls) is str:
        urls = [urls]

    links = OrderedDict()

    for url in urls:
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        content = soup.find('div', id="content")

        topic = OrderedDict()
        for ques in content.find_all("h2", class_="entry-title"):
            link = ques.find("a")

            print(link['href'].strip())
            topic[link.text.strip()] = link['href'].strip()

        if combined:
            links.update(topic)
        else:
            topic_name = url.split('/')[-2].title()
            links[topic_name] = topic

    if not filename:
        print(json.dumps(links, indent=4))
    else:
        with open(filename, "w") as out:
            json.dump(links, out, indent=4)

    print()
    print("Links written to:", filename)


def unique_links(filename):
    with open(filename) as inp:
        data = json.load(inp, object_pairs_hook=OrderedDict)

    uniq = OrderedDict()
    for title, link in data.items():
        if link not in uniq.values():
            uniq[title] = link

    with open(filename, "w") as out:
        json.dump(uniq, out, indent=4)


def list_pages(root_url):

    links = []
    num_pages = 0

    try:
        pq = pyquery.PyQuery(url=root_url)
    except:
        abort("URL doesn't exist.")

    if pq('.pages'):
        num_pages = int(pq('.pages')[0].text.split()[-1])

    if not num_pages:
        num_pages = 1
        print("Only 1 page!")

    for page in range(1, num_pages + 1):
        links.append(URL + f"/page/{page}/")

    return links


if __name__ == '__main__':

    if os.path.isfile(FNAME):
        unique_links(FNAME)
        abort("JSON file already exists: " + FNAME)
    else:
        page_links = list_pages(URL)
        fetch_post_links(page_links, FNAME, combined=True)
        unique_links(FNAME)
