from urllib import request
import urllib.error
from multiprocessing import Pool, Lock
from html.parser import HTMLParser
import argparse
import logging

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
    
    def __init__(self, url, *args, **kwargs):
        super(LinksGetter, self).__init__(*args, **kwargs)
        self.url = url
        self.links = []
      
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
        else:
            if not link.startswith("http"):
                    link = self.url + link
            self.links.append(link)

FETCHED_URLS = set()

def create_resource(link):
    with Lock():
        if link in FETCHED_URLS:
            return None
        FETCHED_URLS.add(link)
    resource = Resource(link)
    resource.data  # we cannot do it lazy here because the BufferReader is not pickable
    return resource

class Resource():
    _size = 0

    url = ""
    request = None
    response = None

    _resources = None
    _data = None
    _size = None

    _processes = 0

    def __init__(self, url, processes=0):
        self.url = url
        FETCHED_URLS.add(url)
        self.request = request.Request(url)
        self._processes = processes
        try:
            self.response = request.urlopen(self.request)
            self.data
            logging.info("url successfull: " + url)
        except urllib.error.HTTPError:
            logging.error("url failed: " + url)
            self._empty()

    def _empty(self):
        """
            Used to clean up the object after an HttpError
        """
        self._resources = []
        self._size = 0
        self._data = ""


    def _get_links(self, html):
        parser = LinksGetter(self.url, str(html))
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
        yield self
        for resource in self.resources:
            for sub_resource in resource.flat_resources_tree():
                yield self, sub_resource

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

    def __repr__(self):
        return self.url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument(
        "-p", "--processes", help="Number of processes to spawn for asyncronous url getter", type=int, default=0,
    )
    args = parser.parse_args()
    url = args.url
    processes = args.processes
    main_resource = Resource(url, processes)
    print(main_resource.size)
    print(main_resource.get_total_size())

