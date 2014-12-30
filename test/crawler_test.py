""" Tests for the crawler module. Includes a basic subclass for testing use. """

import unittest, os, sys

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

    def on_item(self, link, item):
        print 'Item text: {0}'.format(item)


# TODO Add more feeds, and some microblog feeds.
links = [
        'http://127.0.0.1:5000/feed'
        ]
crawler = MyFeedCrawler(links, start_now=True)
