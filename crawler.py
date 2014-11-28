""" Crawls feeds that are of interest to the user. """

from lxml import etree

import requests
from datetime.datetime import now


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
        self._crawling_times = []
        self._start_time = start_time
        self._stop_crawling = start_now
        self._deep_traverse = deep_traverse
        self._errors = []
        if start_now:
            self._do_crawl()

    # Progress Modifiers

    def start():
        """ Starts the crawling process. """
        self.stop_crawling = False

    def stop():
        """ Gracefully stops the crawling process. """
        self.stop_crawling = True

    def progress():
        """ Returns the crawlers progress through its given list. """
        return self._current_step / len(self._links)

    # Status Callbacks

    def on_start():
        """ Called when the crawler is starting up or has finished and is
        going back over the feeds again.

        Passing a list back from this function will set the crawler's
        feed parsing list to that list. """
        pass

    def on_finish():
        """ Called when the crawler has finished crawling the required
        feeds. """
        pass

    def on_data(data):
        """ Called when new data is recieved from a url. The data has not
        yet been parsed and is just text. """
        pass

    def on_feed(feed):
        """ Called when a new feed is just received. Currently does not
        get called at all. """
        pass

    def on_info(info):
        """ Called when a new info field is found in the feed.
        (i.e. relocate, user_name, etc) """
        pass

     def on_item(item):
        """ Called when a new post element is found. """
        pass

   def on_error(error):
        """ Called when an error is encountered. The error contains
        the url of the feed that caused the error and the code of
        the error. """
        print '''Error: {0}
        Code: {1}
        URL: {3}
        '''.format(error['description'], error['code'], error['link'])

    # Internals

    def _do_crawl():
        """ Starts the crawling engine. The engine constantly runs. To stop it,
        use the stop method provided. """
        while not self.stop_crawling:
            # Check for new links.
            new_links = self.on_start()
            if isinstance(new_links, list):
                self._links = new_links

            # Crawl each link.
            for link in self._links:
                self._crawl_link(link)

            self.on_finish()

    def _crawl_link(link):
        """ Crawls...Signals passed to the Crawler will affect the crawling. """
        # Get the feed and parse it.
        r = requests.get(link)
        if not r.status_code == 200:
            error = {
                'link': link,
                'code': r.status_code,
                'description': 'Bad request'
            }
            self.on_error(error)
            continue
        self.on_data(r.text)

        tree = None
        try:
            tree = etree.parse(r.text)
        except ParseError:
            # TODO Add additional, more costly parsers here.
            error = {
                    'link': link,
                    'code': r.status_code,
                    'description': 'Parsing error. Malformed feed.'
                }
            self.on_error(error)
            continue

        # TODO This could be dangerous! The feed could be huge.
        #self.on_feed(self._to_dict(tree))

        # Extract the useful info from it.
        channel = tree.xpath('//channel')
        element_count = 0
        if channel is not None:
            for element in channel.xpath('child::node()'):
                element_count += 1
                if 'item' == element.xpath('name()'):
                     self.on_item(self._to_dict(element))
                else:
                    self.on_info(self._to_dict(element))

                # Check how many elements have been examined in the
                # feed so far, if its too many, break out.
                if element_count > 1000:
                    error = {
                        'link': link,
                        'code': 1000,
                        'description': 'Overflow of elements.'
                        }
                    self.on_error(error)
                    break
        else:
            error = {
                'link': link,
                'code': -1,
                'description': 'No channel element found for link.'
                }
                self.on_error(error)

        # Traverse the next_node of the feed.
        next_node = channel.xpath('/next_node')
        if next_node is not None:
            next_link = next_node.text

            # Check if this is the first node.
            head_node = channel.xpath('/link')
            is_first_node = head_node == link

            if is_first_node or self._deep_traverse:
                self._crawl_link(new_link)

    def _to_dict(element):
        """ Converts a lxml element to python dict.
        See: http://lxml.de/FAQ.html """
        return element.tag, \
            dict(map(self._to_dict, element)) or element.text


