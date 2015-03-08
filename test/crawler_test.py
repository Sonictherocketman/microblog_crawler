""" Tests for the crawler module. Includes a basic subclass for testing use. """

import unittest, os, sys, time, signal
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def __init__(self, links, start_now=False):
        self.total_time = 0
        FeedCrawler.__init__(self, links, start_now=start_now)

    def on_start(self):
        self.total_time = time.time()

    def on_finish(self):
        print 'This iteration took {0} seconds.'.format(time.time() - self.total_time)

    def on_item(self, link, info, item):
        print 'Item text: {0}\n{1}'.format(info, item)
        pass

    def on_error(self, link, error):
        print 'Error for {}:\n {}'.format(link, error)


# TODO Add more feeds, and some microblog feeds.
links = [
        # RSS Feeds
        'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml',
        'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        'http://feeds.bbci.co.uk/news/technology/rss.xml',
        # Microblog feeds
        'http://microblog.brianschrader.com/feed'
        ]
crawler = MyFeedCrawler(links)

def signal_handler(signal, frame):
    crawler.stop()
signal.signal(signal.SIGINT, signal_handler)

crawler.start()
