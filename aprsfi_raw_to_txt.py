#!/usr/bin/env python

import sys
import re
import urllib
from HTMLParser import HTMLParser


def raw_lines(url):
    html = urllib.urlopen(url).read().replace("\xc2\xa0", " ")
    hp = HTMLParser()

    lines = re.findall(r"^.*?'raw_line'.*?$", html, re.M)

    return map(lambda x: hp.unescape(re.sub(r"<[^<]+?>", "", x)), lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python %s <url>" % sys.argv[0]
        sys.exit()

    for line in raw_lines(sys.argv[1]):
        print line
