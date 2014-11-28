""" Tests for the crawler module. Includes a basic subclass for testing use. """

import unittest, os, sys

sys.path.append(os.path.abspath('..'))
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def on_start(self):
        print 'Starting up...'

    def on_finish(self):
        print 'Finished parsing, starting over.'

    def on_data(self, data):
        print 'Progress: {0}'.format(self.progress())
        print 'Sample output: {0}...' .format(data[:20])

    def on_info(self, info):
        print 'Info text: ' + info

    def on_item(self, item):
        print 'Item text: {0}'.format(item)


# TODO Add more feeds, and some microblog feeds.
links = [
        'http://brianschrader.com/rss',
        'http://www.marco.org/rss',
        'http://inessential.com/xml/rss.xml'
        ]
crawler = MyFeedCrawler(links, start_now=True)





