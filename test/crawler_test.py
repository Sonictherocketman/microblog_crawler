""" Tests for the crawler module. Includes a basic subclass for testing use. """

import unittest, os, sys
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def on_start(self):
        pass

    def on_finish(self):
        pass

    def on_data(self, link, data):
        pass

    def on_info(self, link, info):
        pass

    def on_item(self, link, info, item):
        print 'Item text: {0}\n{1}'.format(info, item)
        pass

    def on_error(self, link, error):
        print 'Error for {}:\n {}'.format(link, error)

# TODO Add more feeds, and some microblog feeds.
links = [
        #'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml',
        #'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        #'http://feeds.bbci.co.uk/news/technology/rss.xml'
        #'http://localhost:5000/feed',
        'http://microblog.brianschrader.com/feed'
        ]
crawler = MyFeedCrawler(links, start_now=True)
