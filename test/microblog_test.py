""" A test of various public microblog feeds. """

import unittest, os, sys, time, signal
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def on_item(self, link, info, item):
        """ Prints new items. """
        print '{} says "{}"\t{}'.format(info.username, item.description, item.pubDate)

links = [
        # Brian's Microblog
        #'http://microblog.brianschrader.com/feed',
        'http://127.0.0.1:5000/jjjschmidt/feed.xml',
        'http://macroblog.bigprob.net/?format=rss'
        ]

def signal_handler(signal, frame):
    crawler.stop()
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    MyFeedCrawler(links, start_now=True)

