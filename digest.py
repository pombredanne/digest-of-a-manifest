#!/usr/bin/python2

"""
This script takes at least one argument: path to a file with manifest.
It then computes and prints digest of the manifest(s).
"""

import os
import re
import sys
import json
import hashlib

from collections import OrderedDict


def prepare_file_hack(manifest):
    """
    This is a hacky implementation which removes 'signatures' using regular expressions,
    for more info see:

        https://github.com/docker/distribution/issues/1065

    fd: file object returned by open
    """
    # 0 start -> signatures
    # 1 signatures
    # 2 after signatures
    states = 0
    sig_re = r'(\s+)\"signatures\":\s*\['
    stop = None

    ls = []

    for line in manifest.split("\n"):
        if line == stop:
            states = 2
        if states == 1:
            continue
        m = re.match(sig_re, line)
        if m is not None:
            states = 1
            ls = ls[:-1]
            stop = m.groups()[0] + "]"
            continue
        else:
            ls.append(line)
    return "\n".join(ls)


def prepare_file_decode(manifest):
    """
    Remove 'signatures' by deserializing json

    fd: file object returned by open
    """
    decoded_json = json.loads(manifest, object_pairs_hook=OrderedDict, encoding="utf-8")
    del decoded_json["signatures"]
    # for h in decoded_json["history"]:
    #     # print json.loads(h["v1Compatibility"], object_pairs_hook=OrderedDict, encoding="utf-8")
    #     i = h["v1Compatibility"]
    #     i = i.replace(r"\u003c", "<").replace(r"\u003e", ">").replace(r"\u0026", "&")
    #     h["v1Compatibility"] = i
    #     # print i

    encoded_json = json.dumps(decoded_json, indent=3, separators=(',', ': '), ensure_ascii=False)

    # encoded_json = encoded_json.replace("<", r"\\u003c").replace(">", r"\\u003e").replace("&", r"\\u0026")

    return encoded_json.encode("utf-8")
    return unicode(encoded_json).encode("utf-8")


def compute_digest(manifest):
    """
    E.g.

    sha256:3bd99e8c083e6bb60ef9c1e7de1a2c34a1fab103b6ee4e9c23f08abd91fb6d53

    manifest: str
    """
    return "sha256:" + hashlib.sha256(manifest).hexdigest()


def main():
    if len(sys.argv[1:]) <= 0:
        print "Provide please at least one path to a file with manifest."
        sys.exit(1)
    result = []
    for fp in sys.argv[1:]:
        p = os.path.abspath(os.path.expanduser(fp))
        with open(p, "r") as fd:
            raw_manifest = fd.read()
            content = prepare_file_decode(raw_manifest)
            digest = compute_digest(content)
            result.append((fp, digest))
    if len(result) == 1:
        print result[0][1]
    else:
        for r in result:
            print "{} {}".format(*r)
    sys.exit(0)


if __name__ == "__main__":
    main()
