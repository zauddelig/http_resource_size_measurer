#!/usr/bin/python3
# this is a stub! don't expect it to work, most of all the html parse is still untested and will likely break
from urllib import request
import urllib.error
from multiprocessing import Pool, Lock
from html.parser import HTMLParser
import argparse
import logging
import re
from time import time

class WrongCondition(Exception):
    pass

class LinksGetter(HTMLParser):
    tags = {
      "img": ("src", []),
      "iframe": ("src", []),
      "script": ("src", []),
      "link": ("href", [("rel", "stylesheet"), ]),
    }
    links = None
    url = ""
    regex = re.compile("^(https?:)//")
    def __init__(self, url, *args, **kwargs):
        super(LinksGetter, self).__init__(*args, **kwargs)
        self.url = url
        self.links = []

    @staticmethod
    def parse_dotted_path(link):
        """
        This function takes a string with unix like dots:
        "first/../second"
        and return the effective path
        "second"
        """
        splitted = link.split("/")
        while True:
            try:
                index = splitted.index("..") - 1
            except ValueError:
                break
            if index <= 0:
                return None
            splitted.pop(index)
            splitted.pop(index)
        link = "/".join(splitted)
        return link

    def parse_relative_url(self, link):
        """
            partial implementation of http://www.ietf.org/rfc/rfc1808.txt
        """
        match = self.regex.search(self.url)
        protocol = match.group(0)
        url = self.url[len(protocol):]
        url = url[-1] == "/" and url[:-1] or url
        if link.startswith("//"):
            link = protocol[:-2] + link
        elif link.startswith("/"):
            domain = url.split("/")[0]
            link = protocol + self.parse_dotted_path(domain + link)
        else:
            link = protocol + self.parse_dotted_path(url + "/" + link)
        return link

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        try:
            attr, conditions = self.tags[tag]
            link = attrs[attr]
            for condition, value in conditions:
                if not attrs[condition] == value:
                    raise WrongCondition
        except (KeyError, WrongCondition):
            return

        if not self.regex.search(link):
            link = self.parse_relative_url(link)
        self.links.append(link)

FETCHED_URLS = set()

def create_resource(link):
    with Lock():
        if not link or link in FETCHED_URLS:
            return None
        FETCHED_URLS.add(link)
    resource = Resource(link)
    return resource

class Resource():
    _size = 0

    url = ""
    request = None
    response = None
    time = 0

    _resources = None
    _data = None
    _size = None
    _processes = 0

    def __init__(self, url, processes=0):
        if not url.startswith("http"):
            url = "http://" + url
        self.url = url
        FETCHED_URLS.add(url)
        self.request = request.Request(url)
        self._processes = processes
        try:
            self._make_request()
            logging.info("url successfull: " + url)
        except urllib.error.HTTPError:
            logging.error("url failed: " + url)
            self._empty()

    def _make_request(self):
        start = time()
        self.response = request.urlopen(self.request)
        self.data
        self.time = time() - start

    def _empty(self):
        """
            Used to clean up the object after an HttpError
        """
        self._resources = []
        self._size = 0
        self._data = ""


    def _get_links(self, html):
        parser = LinksGetter(self.url, strict=False)
        parser.feed(str(html))
        return parser.links

    @property
    def data(self):
        if self._data is None:
            self._data = self.response.read()
        return self._data

    def _map(self, f, *iterables):
        if self._processes > 1:
            pool = Pool(self._processes)
            items = [item for item in pool.map(f, *iterables) if item is not None]
            pool.terminate()
            pool.join()
        else:
            items = [item for item in map(f, *iterables) if item is not None]
        return items

    @property
    def size(self):
        if self._size is not None:
            return self._size
        self._size = int(self.response.headers.get("Content-Length", 0) or len(self.data))
        return self._size

    @property
    def resources(self):
        if self._resources is None:
            if "html" in self.response.headers["Content-Type"]:
                links = self._get_links(self.data)
                self._resources = self._map(create_resource, links)
            else:
                self._resources = []
        return self._resources


    def flat_resources_tree(self):
        """
            Return the resources in a flat iterator
        """
        yield self
        for resource in self.resources:
            for sub_resource in resource.flat_resources_tree():
                yield sub_resource

    def piramid_tree(self):
        """
            Return the resources pyramid iterator
        """
        yield (self, )
        for resource in self.resources:
            for sub_resource in resource.flat_resources_tree():
                yield self, sub_resource

    def get_mean_time(self):
        """
            Return the harmonic mean of the resources
        """
        mean_time = self.time / self.size
        resources = tuple(self.flat_resources_tree())
        length = len(resources) + 1
        for resource in resources:
            mean_time +=  resource.size and resource.time / resource.size  or 0
        return length/mean_time

    def get_total_size(self):
        """
            Return the total size of the resources tree
        """
        size = 0
        for resource in self.flat_resources_tree():
            size += resource.size
        return size

    def get_links_count(self):
        return len(list(self.resources))

    def __str__(self):
        return "%s,%ss,%sB" %(self.url, self.time, self.size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url you want to study")
    parser.add_argument(
        "-p", "--processes", help="Number of processes to spawn for asyncronous url getter", type=int, default=0,
    )
    parser.add_argument(
        "-T", "--tree", action='store_true',
        help="Print the resources tree, each resource is represented by a tuple of url, time, size",
    )
    args = parser.parse_args()
    url = args.url
    processes = args.processes
    main_resource = Resource(url, processes)
    if args.tree:
        for branch in main_resource.piramid_tree():
            point, branch= branch[-1], branch[:-1]
            print("".join("\t" for e in branch) + str(point).replace(",", ",\t"))
    print("Total size:\t%sB\nMean Speed:\t%sB/s" % (main_resource.get_total_size(), main_resource.get_mean_time()))

