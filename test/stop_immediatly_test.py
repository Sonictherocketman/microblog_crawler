""" A crawler that stops quickly. """

import unittest, os, sys, time, signal
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def __init__(self, links, start_now=False):
        FeedCrawler.__init__(self, links, start_now=start_now)

    def on_error(self, link, error):
        print 'Error: {}\n{}'.format(error['description'], link)

    def on_item(self, link, item):
        print item.description

    def on_finish(self):
        print 'STOPPING NOW'
        self.stop(now=True)


links = [
        'http://localhost:5000/jjjschmidt/feed.xml',
        'http://microblog.brianschrader.com/feed',
        'http://macroblog.bigprob.net/?format=rss'
        ]


if __name__ == '__main__':
    crawler = MyFeedCrawler(links)
    crawler.start()




