from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import urlopen
import sys


class Analyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tags, attrs):
        if tags == "a":
            for k, v in attrs:
                if k == "href":
                    self.links.append(v)

def spider(start_url):
    todo = [start_url]
    seen = set()

    while len(todo) > 0:
        bu = todo.pop()

        bu_split = list(urlparse(bu))
        bu_split[5] = ""
        bu = urlunparse(bu_split)

        if bu in seen:
            continue
        seen.add(bu)

        print(bu, end=" ")

        try:
            f = urlopen(bu)
        except HTTPError:
            print("<failed to load>")
            continue
        d = f.read()
        f.close()

        ct = f.info()["Content-Type"]
        if ct is None or not ct.startswith("text/html"):
            print("<skipping>")
            continue

        an = Analyzer()
        an.feed(str(d))

        for l in an.links:
            full_url = urljoin(bu, l)
            if not full_url.startswith(start_url):
                continue

            todo.append(full_url)

        print("<processed %d links>" % len(set(an.links)))
    print("Total: %s links" % len(seen))

spider(sys.argv[1])
