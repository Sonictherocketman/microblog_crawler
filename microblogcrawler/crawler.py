""" Crawls feeds that are of interest to the user. """

from lxml import etree
from io import StringIO, BytesIO
import requests
from datetime import datetime, timedelta
import pytz
from dateutil.parser import parse
import time
from multiprocessing import Pool


# Public FeedCrawler Class


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
        self._crawl_data = []
        self._start_time = start_time
        self._stop_crawling = not start_now
        self._deep_traverse = deep_traverse
        self._pool = Pool(7)
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
            start_time = datetime.now(pytz.utc)
            start_time.replace(microsecond=0)

        self._update_data()

        # Start crawling.
        while not self._stop_crawling:
            # Check for new links.
            new_links = self.on_start()
            if isinstance(new_links, list):
                self._links = new_links
                self._update_data()
            # Crawl the links.
            self._pool.apply_async(self._crawl_link(), self._links, self._process)
            self.on_finish()
            # TODO: Derive new sleep timer. this will not work async.
            time.sleep(1)

        # Clean up and shut down.
        self._links = []
        self._start_now = False
        self.on_shutdown()

    def _process(self, link, data, updated_cache, error):
        """ Callback to handle the _crawl_link data once it's
        returned from processing. This is called for each link once
        it returns. """
        # Process the data
        raw = data['raw']
        info_fields = data['info_fields']
        items = data['items']

        # Notify self that raw data was found.
        self.on_data(raw)
        # Notify self that info fields were found.
        self.on_info(info) for info in info_fields
        # Notify self that new items were found.
        self.on_item(item) for item in items

        # Get the link's crawl_data
        crawl_time = data['crawl_time']

        # Prune the expired posts from the cache.
        for i, expire_time in updated_cache['expire_times']:
            if crawl_time > expire_time:
                del updated_cache['descriptions'][i]
                del updated_cache['expire_times'][i]

        # Update the crawl_data.
        new_crawl_data = link, crawl_time, updated_cache, self._deep_traverse, False
        index = [i for i, alink in self._links if alink == link][0]
        self._crawl_data[index] = new_crawl_data

    def _update_data(self):
        """ Updates the internal data for each link. """
        new_crawl_data = []
        old_links = [index, old_link for index, old_link, lct, c, dt, ifp in self._crawl_data]
        for index, link in self._links:
            for old_link, lct, c, dt, ifp in self._crawl_data:
                if link == old_link:
                    # If the link is already in the crawl data.
                    if link in old_links:
                        data = old_link, lct, c, dt, ifp
                        new_crawl_data.insert(index, data)
                    # Add a new entry.
                    else:
                        last_crawl_time = datetime.now(pytz.utc)
                        cache = { 'expire_times': [], 'descriptions': [] }
                        deep_traverse = self._deep_traverse
                        is_first_pass = True

                        data = link, last_crawl_time, cache, deep_traverse, is_first_pass
                        new_crawl_data.insert(index, data)
        self._crawl_data = new_crawl_data


# Internal Crawling Function


def _crawl_link(link, last_crawl_time, cache, deep_traverse, is_first_pass):
    """ Performs the actual crawling. """
    # Record the time the link was fetched.
    fetch_time = datetime.now(pytz.utc)
    fetch_time.replace(second=0, microsecond=0)

    data = { 'info_fields': [], 'items': [], 'raw': '', 'crawl_time': None }

    # Get the feed and parse it.
    try:
        r = requests.get(link)
    except: requests.exceptions.ConnectionError:
        return link, data, cache, { 'code': -1, 'description': 'Connection refused' }

    # Check if the request went through and begin parsing.
    if r.status_code != 200:
        return link, data, cache, { 'code': r.status_code, 'description': 'Bad request' }

    data['raw'] = r.text

    try:
        tree = etree.parse(BytesIO(r.content))
    except etree.ParseError:
        # TODO Add additional, more costly parsers here.
        return link, data, cache, { 'code': -1, 'description': 'Parsing error, malformed feed.' }

    # Extract the useful info from it.
    element_count = 0
    channel = tree.xpath('//channel')
    if len(channel) < 1:
        return link, data, cache, { 'code': -1, 'description': 'No channel element found.' }

    for element in channel[0].getchildren():
        element_count += 1
        # Search for info fields.
        if element.xpath('name()').lower() != 'item':
            info = _to_dict(element)
            if info not None:
                data['info_fields'].append(info)
        # Search for items.
        else:
            item = _to_dict(element)[1]
            if item is not None:
                # Get the pubdate of the item.
                # If the pubdate has no tzinfo, the server's timezone.
                pubdate = parse(item['pubdate'])
                if pubdate.tzinfo is None:
                    server_time = parse(r.headers['date'])
                    server_tz = pytz.timezone(server_time.tzname())
                    pubdate = server_tz.localize(pubdate)
                # Normalize timezones to UTC
                pubdate = pytz.utc.normalize(pubdate)
                item_is_new = pubdate >= last_crawl_time \
                        and item['description'] not in cache['descriptions']
                if is_first_pass or item_is_new:
                    # Cache the item's text and when it expires from the cache.
                    cache[link]['descriptions'].append(item['description'])
                    cache[link]['expire_times'].append(datetime.now(pytz.utc) + timedelta(0, 3))
                    # Add it to the list of new items.
                    data['items'].append(item)

        # Check how many elements have been examined in the
        # feed so far, if its too many, break out.
        if element_count > FeedCrawler.MAX_ITEMS_PER_FEED:
            return link, data, cache, { 'code': -1, 'description': 'Overflow of elements.' }

    # Traverse the next_node of the feed.
    next_node = tree.xpath('//next_node')
    if next_node is not None and len(next_node) > 0:
        next_link = next_node[0].text
        # Check if this is the first node.
        head_node = channel.xpath('/link')
        is_first_node = head_node == link
        if is_first_node or deep_traverse or is_first_pass:
            _crawl_link(new_link, last_crawl_time, cache, deep_traverse, is_first_pass)

    # Update the stored crawl time to the saved value above.
    data['crawl_time'] = fetch_time
    return link, data, cache, None


def _to_dict(element):
    """ Converts a lxml element to python dict.
    See: http://lxml.de/FAQ.html """
    return element.tag.lower(), \
        dict(map(_to_dict, element)) or element.text

