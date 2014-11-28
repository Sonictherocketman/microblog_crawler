""" Tests for the crawler module. Includes a basic subclass for testing use. """

from microblogcrawler.crawler import FeedCrawler

import unittest


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def on_start():
        print 'Starting up.'

    def on_finish():
        print 'Shutting down.'

    def on_data(data):
        print 'Sample output: {0}...' .format(data[:20])

    def on_info(info):
        print 'Info text: {0}'.format(info)


class FeedCrawlerTest(unittest.TestCase):

    def setUp(self):
        # TODO Add more feeds, and some microblog feeds.
        links = [
                'http://brianschrader.com/rss',
                'http://www.marco.org/rss'
                ]
        self.crawler = MyFeedCrawler(links, start_now=True)





