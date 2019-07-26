#!/usr/bin/env python3.6
"""
Run Pandoc to convert an HTML to PDF.

Usage: html_to_pdf [options] <src>

Options:

    -t --tex         Convert to PDF instead of tex
    -f --force       Overwrite destination
    -v --verbose     Make pandoc be verbose
"""

import os

import subprocess

from docopt import docopt
import json
from collections import OrderedDict
import os.path
import re
import sys
import string

from download_html import mkdir, ROOT as ROOT_TOPICS
from download_total import subtract_header, HEADS

ROOT_PDF = "PDF"
ROOT_TEX = "TEX"
ROOT_MEDIA = os.path.join(ROOT_TEX, "MEDIA")
SUB_TEX = os.path.join(ROOT_TEX, "SUB")

pandoc_options = [
    "/usr/bin/pandoc",
    "--quiet",

    "--pdf-engine", "xelatex",

    "--toc",
    "-V", "tables",
    "-V", "graphics",

    "-V", "geometry:margin=1.5in",
    "-V", "documentclass=article",
    # "-V" "geometry:papersize=a3paper",

    "-V", "urlcolor=blue",
    "-V", "linkcolor=blue",
]

def pandoc_base(src, dst=None, template="template.tex", from_file=True,
        from_type="html", to_type="latex", verbose=False, print_cmd=False,
        standalone=False, title="", media_dir="", other_args=[]):

    command = pandoc_options.copy()
    if verbose:
        command[command.index("--quiet")] = "--verbose"
    if template:
        command.append("--template=%s" % template)
    if standalone:
        command.append("-s")

    if title:
        command += ["-V", "title=%s" % title]

    if media_dir:
        command.append("--extract-media=%s" % media_dir)

    command += other_args

    # Use src as the input content if not running from file
    if from_file:
        input_content = None
        command += [src]
    else:
        input_content = src.encode('utf-8')
        command += ["-f", from_type]

    # If dst is empty then return the content as a string
    if dst:
        stdout = None
        command += ["-o", dst]
    else:
        stdout = subprocess.PIPE
        command += ["-t", to_type]

    if print_cmd:
        print(" ".join(command))
    print('*'*100, input_content, stdout, command)
    ret = subprocess.run(command, input=input_content, stdout=stdout, stderr=sys.stderr)
    sys.stderr.write(ret.stderr.decode())
    if not dst:
        return ret.stdout.decode()

def topic_filename(json_keys, root=ROOT_TOPICS):
    return os.path.join(root, "/".join(json_keys[1:]))

def json_keys(json_dict):
    return _json_keys(json_dict)

def _json_keys(json_dict, path=[]):
    if not len(json_dict):
        return []
    paths = []
    if path:
        paths.append(tuple(path))
    if isinstance(json_dict, OrderedDict):
        for k, v in json_dict.items():
            if isinstance(v, str):
                paths.append(tuple(path + [v.split("/")[-2] + ".html", k]))
            else:
                paths += _json_keys(v, path + [k])
    return paths

def sublist(path1, path2):
    return len(path1) < len(path2) and all(p1 == p2 for p1, p2 in zip(path1, path2))

def sanitize(fname):
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    fname = fname.replace(" ", "_")
    return ''.join(c for c in fname if c in valid_chars)

def generate_multifile_pdf(src, texfile, dst, force=False, verbose=False):
    if not force and os.path.isfile(dst):
        print("Destination already exists.")
        return

    title = os.path.splitext(os.path.basename(src))[0]
    if not force and os.path.isfile(texfile):
        print("Temporary TeX file already exists, generating PDF.")
    else:
        with open(src, 'r') as src, open(texfile, 'w+') as texf:
            jdict = json.load(src, object_pairs_hook=OrderedDict)
            keys = json_keys(jdict)
            jkeys = list(jdict.keys())
            title = jkeys[0] if len(jkeys) == 1 else title  # The top level element if there is anything

            # template_placeholder = "(BODY)"
            # template = pandoc_base(template_placeholder, from_file=False,
            #     ).split(template_placeholder)

            # texf.write(template[0])  # Write first half of template

            for i, key in enumerate(keys):
                if i + 1 >= len(keys) or not sublist(key, keys[i+1]):
                    fname = topic_filename(key[:-1])
                    print("Reading %s" % fname)
                    tex_basename = sanitize(os.path.basename(topic_filename(key[:-1], ROOT_TEX).replace(".html", ".tex")))
                    tex_fname = os.path.join(SUB_TEX, str(len(key)-2) + "--" + tex_basename)
                    if not os.path.isfile(fname):
                        print("Source HTML %s doesn't exist, skipping" % fname)
                    else:
                        input_statement = "\n\\input{%s}\n" % os.path.relpath(tex_fname)
                        texf.write(input_statement)
                        if not force and os.path.exists(tex_fname):
                            print("Output TeX %s exists, skipping" % tex_fname)
                        else:
                            content = subtract_header(open(fname, 'r').read(), len(key)-3)
                            mkdir(SUB_TEX)
                            tex_content = pandoc_base(
                                content, from_file=False, template=None,
                                verbose=verbose, media_dir=ROOT_MEDIA
                            )
                            # Filter removes all .shtml graphics since these don't work
                            tex_content = re.sub(r"\\includegraphics(?:\[.*\])?{.*.shtml}", r"\mbox{Image unavailable}", tex_content)
                            with open(tex_fname, 'w+') as texf_small:
                                texf_small.write(tex_content)
                elif len(key) > 1:
                    content = "<h{}>".format(len(key)-1) + key[-1] + "</h{}>".format(len(key)-1)
                    texf.write("\n" + pandoc_base(content, from_file=False, template=None, verbose=verbose) + "\n")
                elif len(key) > 0:
                    title = key[-1]
            # texf.write(template[1])  # Write second half of template

    print("Producing PDF")
    pandoc_base(texfile, dst, verbose=verbose, standalone=True, title=title)

def generate_pdf(src, dst, force=False, verbose=False):

    # If source doesn't exist or destination already does
    if not os.path.isfile(src):
        print("Source HTML doesn't exist")
        return

    if not force and os.path.isfile(dst):
        print("Destination already exists.")
        return

    title = os.path.basename(src)
    title = title[0:title.rfind(".")]

    # Run in verbose mode when converting from a .tex to .pdf
    # because one would only do this when shit has gone wrong
    pandoc_base(src, dst, verbose=verbose or src.endswith(".tex"))

if __name__ == '__main__':

    args = docopt(__doc__)

    src = os.path.basename(args['<src>'])

    if args['--tex']:
        dst = src.replace(".html", ".tex")
    else:
        dst = src.replace(".html", ".pdf").replace(".tex", ".pdf")

    if src.endswith(".json"):
        generate_multifile_pdf(
            src=args['<src>'],
            texfile=os.path.join(ROOT_TEX, src.replace(".json", ".tex")),
            dst=os.path.join(ROOT_PDF, src.replace(".json", ".pdf")),
            force=args["--force"],
            verbose=args["--verbose"]
        )
    else:
        generate_pdf(
            src=args['<src>'],
            dst=os.path.join(ROOT_PDF, dst),
            force=args["--force"],
            verbose=args["--verbose"]
        )
