""" Crawls feeds that are of interest to the user. """

from lxml import etree
from io import StringIO, BytesIO
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import time


class FeedCrawler():
    """ A crawler for Microblog and RSS XML feeds. Similar to the
    Tweepy StreamListener, this crawler will traverse the list of
    feeds it is given and once finished, will traverse them again.
    Subclass FeedCrawler to fill in the callbacks you need.

    The crawler will use the `deep_traverse` flag to determine
    whether it should continue parsing `next_node` links in the feed.
    By default, the crawler will traverse the link it is given and one
    page back (if it exists).

    If not provided a start time, the crawler will callback whenever any
    item is found in the feed, regardless of when it was posted. The
    time provided will act as a 'from this time forward' flag. """

    MAX_ITEMS_PER_FEED = 1000

    def __init__(self, links, start_now=False, start_time=None, deep_traverse=False):
        """ Creates a new crawler.
        - To start the crawler immediately,
        pass a `start_now` value.
        - To get all posts from a feed after a certain time, set
        a desired `start_time` value. Otherwise all elements in a
        given feed will be provided.
        - To traverse the entire user's feed, set `deep_traverse`
        to True. """
        self._links = links
        self._current_step = 0
        self._crawl_times = {}
        self._start_time = start_time
        self._is_first_pass = True
        self._stop_crawling = not start_now
        self._deep_traverse = deep_traverse
        self._errors = []
        self._cache = {}
        if start_now:
            self._do_crawl()

    # Progress Modifiers

    def start(self, links=None):
        """ Starts the crawling process. """
        if links is not None:
            self._links = links
        self._stop_crawling = False
        self._do_crawl()

    def stop(self):
        """ Gracefully stops the crawling process. """
        self._stop_crawling = True

    def progress(self):
        """ Returns the crawlers progress through its given list. """
        return self._current_step / len(self._links)

    # Status Callbacks

    def on_start(self):
        """ Called when the crawler is starting up or has finished and is
        going back over the feeds again.

        Passing a list back from this function will set the crawler's
        feed parsing list to that list. """
        pass

    def on_finish(self):
        """ Called when the crawler has finished crawling the required
        feeds. """
        pass

    def on_shutdown(self):
        """ Called when the crawler has recieved a shutdown mesage. This
        method is the last thing the crawler does before shutting down. """
        pass

    def on_data(self, link, data):
        """ Called when new data is recieved from a url. The data has not
        yet been parsed and is just text. """
        pass

    def on_feed(self, link, feed):
        """ Called when a new feed is just received. Currently does not
        get called at all. """
        pass

    def on_info(self, link, info):
        """ Called when a new info field is found in the feed.
        (i.e. relocate, user_name, etc) """
        pass

    def on_item(self, link, item):
        """ Called when a new post element is found. """
        pass

    def on_error(self, link, error):
        """ Called when an error is encountered. The error contains
        the url of the feed that caused the error and the code of
        the error. """
        print '''Error: {0}
        Code: {1}
        URL: {2}
        '''.format(error['description'], error['code'], error['link'])

    # Internals

    def _do_crawl(self):
        """ Starts the crawling engine. The engine constantly runs. To stop it,
        use the stop method provided. """
        # Set all the starting crawl times.
        start_time = None
        if self._start_time is not None:
            start_time = self._start_time
        else:
            start_time = datetime.now()
            start_time.replace(microsecond=0)
        for link in self._links:
            self._crawl_times[link] = start_time

        # Start crawling.
        while not self._stop_crawling:
            # Check for new links.
            new_links = self.on_start()
            if isinstance(new_links, list):
                self._links = new_links

            for link in self._links:
                # Add the links to the cache if they aren't already.
                if link not in self._cache.keys():
                    self._cache[link] = {'expire_times': [], 'descriptions': []}

                # Crawl the link.
                if self._stop_crawling:
                    break
                self._crawl_link(link)

                # Clear the cache for the link.
                for i, expire_time in enumerate(self._cache[link]['expire_times']):
                    if self._crawl_times[link] > expire_time:
                        del self._cache[link]['descriptions'][i]
                        del self._cache[link]['expire_times'][i]

            # Get ready to go again.
            if self._is_first_pass:
                self._is_first_pass = False
            self.on_finish()

            time.sleep(1)

        # Clean up and shut down.
        self._links = []
        self._start_now = False
        self.on_shutdown()

    def _crawl_link(self, link):
        """ Crawls...Signals passed to the Crawler will affect the crawling. """
        # Record the time the link was fetched.
        fetch_time = datetime.now().replace(second=0, microsecond=0)

        # Get the feed and parse it.
        r = None
        try:
            r = requests.get(link)
        except requests.exceptions.ConnectionError:
            print 'Connection refused:' + link
            return

       # Check if the request went through and begin parsing.
        if not r.status_code == 200:
            error = {
                'link': link,
                'code': r.status_code,
                'description': 'Bad request'
            }
            self.on_error(link, error)
            return
        self.on_data(link, r.text)

        tree = None
        try:
            tree = etree.parse(BytesIO(r.content))
        except etree.ParseError:
            # TODO Add additional, more costly parsers here.
            self.on_error({
                    'link': link,
                    'code': -1,
                    'description': 'Parsing error. Malformed feed.'
                })
            return

        # TODO This could be dangerous! The feed could be huge.
        #self.on_feed(self._to_dict(tree))

        # Extract the useful info from it.
        element_count = 0
        channel = tree.xpath('//channel')
        if len(channel) < 1:
            self.on_error({
                    'link': link,
                    'code': -1,
                    'description': 'No channel element found.'
                })
            return
        for element in channel[0].getchildren():
            element_count += 1
            if 'item' == element.xpath('name()'):
                item = self._to_dict(element)[1]
                if item is not None:
                    # Check if the item is new or if this is the
                    # crawler's first pass over the feed.
                    item_is_new = ('pubdate' in item.keys() \
                            and parse(item['pubdate']) >= self._crawl_times[link]) \
                            and item['description'] not in self._cache[link]['descriptions']
                    if self._is_first_pass or item_is_new:
                        # Cache the item's text and when it expires from the cache.
                        self._cache[link]['descriptions'].append(item['description'])
                        self._cache[link]['expire_times'].append(datetime.now() + timedelta(0, 3))

                        # Call the callback.
                        self.on_item(link, item)
            else:
                info = self._to_dict(element)[1]
                if info is not None:
                    self.on_info(link, info)

            # Check how many elements have been examined in the
            # feed so far, if its too many, break out.
            if element_count > FeedCrawler.MAX_ITEMS_PER_FEED:
                self.on_error({
                    'link': link,
                    'code': -1,
                    'description': 'Overflow of elements.'
                    })
                break

        # Traverse the next_node of the feed.
        next_node = tree.xpath('//next_node')
        if next_node is not None and len(next_node) > 0:
            next_link = next_node[0].text

            # Check if this is the first node.
            head_node = channel.xpath('/link')
            is_first_node = head_node == link

            if is_first_node or self._deep_traverse:
                self._crawl_link(new_link)

        # Update the stored crawl time to the saved value above.
        self._crawl_times[link] = fetch_time

    def _to_dict(self, element):
        """ Converts a lxml element to python dict.
        See: http://lxml.de/FAQ.html """
        return element.tag.lower(), \
            dict(map(self._to_dict, element)) or element.text


