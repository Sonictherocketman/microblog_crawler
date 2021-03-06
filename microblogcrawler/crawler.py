""" Crawls feeds that are of interest to the user. """

from lxml import etree
from io import StringIO, BytesIO
import requests
from datetime import datetime, timedelta
import pytz
from dateutil.parser import parse
import time
from multiprocessing import Pool
import sys
import pkg_resources
from collections import namedtuple

from feed import MainFeed, MalformedFeedError

SimpleUser = namedtuple('User', 'username user_id link')


# Public FeedCrawler Class


class FeedCrawler():
    """ A crawler for valid Microblog XML feeds. Similar to the
    Tweepy StreamListener, this crawler will traverse the list of
    feeds it is given and once finished, will traverse them again.
    Subclass FeedCrawler to fill in the callbacks you need.

    Because FeedCrawler uses the Open-Microblog validator, it only
    successully parses 100% valid microblog-rss feeds.

    The crawler will use the `deep_traverse` flag to determine
    whether it should continue parsing `next_node` links in the feed.
    By default, the crawler will traverse the link it is given and one
    page back (if it exists).

    If not provided a start time, the crawler will callback whenever any
    item is found in the feed, regardless of when it was posted. The
    time provided will act as a 'from this time forward' flag. """

    # How many times should the crawler follow HTTP 301 redirects.
    MAX_REDIRECTS = 10

    # How many items should the crawler attempt to return before
    # admitting that a page of the feed may be too big. This limit
    # resets for each page of the feed. A properly paginated feed
    # should never hit this limit.
    MAX_ITEMS_PER_FEED = 2000

    # Should the crawler allow RSS feeds.
    ALLOW_RSS = False

    # Seconds between crawl attempts. Since the crawler returns feed
    # items whenever it finishes parsing, and does not wait for other
    # feeds to complete this is considered as the most often a given
    # feed will be parsed.
    # Note: The crawler uses a lot of bandwidth. Lowering the crawl time
    # can make the timeline more realtime, but will cost more in bandwidth.
    # For example, crawling every 3 sec for ~60 feeds will use ~0.5TB of
    # bandwidth per month (~750 hrs).
    CRAWL_INTERVAL = 3

    # The number of seconds a given queue can be given to complete
    # it's jobs.
    PROCESSING_TIMEOUT = 5

    # Seconds until cached posts expire. Adjust this range if you
    # notice duplicate items in your feed. Longer expire times mean
    # the cache is more memory intensive to store and computationally
    # expensive to search, and shorter times may result in duplicates.
    #
    # This time should be longer than the CRAWL_INTERVAL.
    CACHE_EXPIRE_TIME = 9

    # The number of worker threads in the pool. This number would
    # typically be the number of cores on your machine. Numbers
    # larger than the number of cores may not improve performance
    # as expected.
    POOL_SIZE = 4

    # Microblog Crawler's User Agent string. We are good citizens of
    # the internet and should provide a useful metric to our followers.
    # The User-Agent contains the count of subscribers that it represents.
    # Sample: `Microblog Feed Crawler/1.1.200 (darwin; 1 subscribers;)`
    USER_AGENT = 'Microblog Feed Crawler/{0} ({1}; {2} subscribers;)'.format(
            pkg_resources.get_distribution('MicroblogCrawler').version,
            sys.platform,
            1)

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
        self._pool = Pool(FeedCrawler.POOL_SIZE)
        if start_now:
            self._do_crawl()


    # Getters and Setters

    def set_links(self, links):
        """ Adds the given links to the crawl list. Using this assures that
        the adding process isn't incomplete. """
        self._links = links
        self._update_data()

    def get_links(self):
        """ Does what it says on the tin. """
        return self._links

    # Progress Modifiers

    def start(self, links=None):
        """ Starts the crawling process. """
        if links is not None:
            self._start_time = datetime.now(pytz.utc)
            self.set_links(links)
        self._stop_crawling = False
        self._do_crawl()

    def stop(self, now=False):
        """ Gracefully stops the crawling process. This shuts down
        the processing pool and exits when all processes have stopped. """
        self._stop_crawling = True
        if now:
            # Try to close the crawler and if it fails,
            # then ignore the error. This is a known issue
            # with Python multiprocessing.
            try:
                self._pool.terminate()
            except Exception as e:
                print e
        else:
            self._pool.close()
        self._pool.join()

        # Test that everything is gone.
        #processes = self._pool._pool
        #self._pool = None
        #for worker in processes:
        #    assert not worker.is_alive()

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
        """ Called when the feed is parsed. Feed is a python feed object
        modeling the entire feed being parsed.
        """
        pass

    def on_item(self, link, user, item):
        """ Called when a new post element is found. """
        pass

    def on_error(self, link, error):
        """ Called when an error is encountered. The error contains
        the url of the feed that caused the error and the code of
        the error. """
        print '''Error: {0}
        Code: {1}
        URL: {2}
        '''.format(error.get('description'), error.get('code'), error.get('link'))

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
            new_links = self.on_start()
            if isinstance(new_links, list):
                self.set_links(new_links)
            results = []
            for crawl_data in self._crawl_data:
                try:
                    results.append(self._pool.apply_async(_crawl_link, crawl_data,
                        callback=self._process))
                except Exception as e:
                    link = crawl_data[0]
                    self.on_error(link, { 'code': -1, 'description': 'Error crawling link.' })
            try:
                [result.get(timeout=FeedCrawler.PROCESSING_TIMEOUT) for result in results]
            except Exception as e:
                print e  # Errors here mean that the pool closed unexpectedly.
            self.on_finish()
            time.sleep(FeedCrawler.CRAWL_INTERVAL)

        # Clean up and shut down.
        self._links = []
        self._start_now = False
        self.on_shutdown()

    def _process(self, return_data):
        """ Callback to handle the _crawl_link data once it's
        returned from processing. This is called for each link once
        it returns. """
        link, data, cache, error = return_data
        raw = data['raw']
        feed = data['feed']
        items = data['items']
        user = SimpleUser(username=feed.username,
                user_id=feed.user_id,
                link=feed.link)

        # Notify self.
        # TODO: Change ERRORS to NamedTuples
        if error is not None:
            self.on_error(link, error)
            return
        self.on_data(link, raw)
        self.on_feed(link, feed)
        [self.on_item(link, user, item) for item in items]

        # Prune the expired posts from the cache.
        crawl_time = data['crawl_time']
        for i, expire_time in enumerate(cache['expire_times']):
            if crawl_time > expire_time:
                del cache['descriptions'][i]
                del cache['expire_times'][i]

        # Update the crawl_data.
        new_crawl_data = link, crawl_time, cache, self._deep_traverse, False, self.ALLOW_RSS
        index = [i for i, alink in enumerate(self._links) if alink == link][0]
        self._crawl_data[index] = new_crawl_data

    def _update_data(self):
        """ Updates the internal data for each link. """
        last_crawl_time = datetime.now(pytz.utc)
        cache = { 'expire_times': [], 'descriptions': [] }
        deep_traverse = self._deep_traverse
        is_first_pass = True

        old_links = [link for link, lct, c, dt, ifp, rss in self._crawl_data]
        # Append new links.
        [self._crawl_data.append((link, last_crawl_time, cache, deep_traverse,
                is_first_pass, self.ALLOW_RSS)) for link in self._links
                if link not in old_links]
        # Remove unused links.
        for i, _ in enumerate(self._crawl_data):
            if self._crawl_data[i][0] not in self._links:
                del self._crawl_data[i]


# Internal Crawling Function


def _crawl_link(link, last_crawl_time, cache, deep_traverse, is_first_pass, allow_rss):
    """ Performs the actual crawling. """
    # This try is based on a workaround for non-pickleable exceptions.
    # http://stackoverflow.com/questions/15314189/python-multiprocessing-pool-hangs-at-join
    try:
        # Record the time the link was fetched.
        fetch_time = datetime.now(pytz.utc)
        fetch_time.replace(second=0, microsecond=0)

        data = { 'feed': None, 'items': [], 'raw': '', 'crawl_time': None }

        # Add various info to the headers.
        headers = { 'User-Agent': FeedCrawler.USER_AGENT }
        if not is_first_pass:
            headers['If-Modified-Since'] = last_crawl_time.strftime('%a, %d %b %Y %H:%M:%S %Z')

        attempts = 0
        new_link = link
        while True:
            # Make the request.
            try:
                r = requests.get(new_link, headers=headers)
            except requests.exceptions.ConnectionError:
                return link, data, cache, { 'code': -1,
                        'description': 'Connection refused' }

            # Check for HTTP status codes.
            if r.status_code == 301:
                attempts += 1
                if attempts < FeedCrawler.MAX_REDIRECTS:
                    new_link = r.headers['Location']
                else:
                    return link, data, cache, { 'code': r.status_code,
                            'description': 'Too many redirects.'}
            elif r.status_code == 304:
                data['crawl_time'] = fetch_time
                return link, data, cache, None
            elif r.status_code == 404:
                return link, data, cache, { 'code': r.status_code,
                        'description': 'Feed not found.' }
            elif r.status_code == 500:
                return link, data, cache, { 'code': r.status_code,
                        'description': 'Internal server error.' }
            elif r.status_code != 200:
                return link, data, cache, { 'code': r.status_code,
                        'description': 'Other error, check HTTP status code.' }
            else:
                break

        data['raw'] = r.text

        try:
            feed = MainFeed(raw_text=r.content, allow_rss=allow_rss)
        except MalformedFeedError as e:
            return link, data, cache, { 'code': -1,
                    'description': str(e) }

        """
        # Check the last build date if this feed has been seen before.
        if not is_first_pass:
            lbd_element = channel[0].xpath('//lastBuildDate')
            if len(lbd_element) > 0:
                last_build_date = parse(lbd_element[0].text)
                if last_build_date < last_crawl_time:
                    data['crawl_time'] = fetch_time
                    return link, data, cache, None
        """
        data['feed'] = feed

        for item in feed:
            # Normalize timezones to UTC
            try:
                pubDate = pytz.utc.normalize(parse(item.pubDate))
                item_is_new = pubDate >= last_crawl_time \
                        and item.description not in cache['descriptions']
                if is_first_pass or item_is_new:
                    # Cache the item's text and when it expires from the cache.
                    expire_time = datetime.now(pytz.utc) \
                        + timedelta(0, FeedCrawler.CACHE_EXPIRE_TIME)
                    cache['descriptions'].append(item.description)
                    cache['expire_times'].append(expire_time)
                    # Add it to the list of new items.
                    data['items'].append(item)
            except ValueError as e:
                # Timezone info not present. Skipping.
                pass
        # Traverse the next_node of the feed.
        next_node = None
        try:
            getattr(item, 'next_node')
        except AttributeError:
            pass
        if next_node is not None:
            # Check if this is the first node.
            is_first_node = head_node == self.link
            if is_first_node or deep_traverse or is_first_pass:
                _crawl_link(item.next_node, last_crawl_time, cache, deep_traverse,
                        is_first_pass)

        # Update the stored crawl time to the saved value above.
        data['crawl_time'] = fetch_time
        return link, data, cache, None
    except Exception as e:
        from traceback import format_exc
        return link, data, cache, { 'code': -1, 'description': 'Error during crawl {0}'.format(format_exc()) }
        pass

def _to_dict(element):
    """ Converts a lxml element to python dict.
    See: http://lxml.de/FAQ.html """
    return element.tag.lower(), \
        dict(map(_to_dict, element)) or element.text

