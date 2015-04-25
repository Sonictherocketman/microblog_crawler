""" A crawler that stops quickly. """

import unittest, os, sys, time, signal
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def __init__(self, links, start_now=False):
        FeedCrawler.__init__(self, links, start_now=start_now)

    def on_finish(self):
        print 'STOPPING NOW'
        self.stop(now=True)


links = [
        'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml',
        'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'http://www.marco.org/rss',
        'http://daringfireball.net/feeds/',
        'http://inessential.com/xml/rss.xml',
        'http://brianschrader.com/rss',
        'http://david-smith.org/atom.xml',
        'http://globalspin.com/feed'
        ]


if __name__ == '__main__':
    crawler = MyFeedCrawler(links)
    crawler.start()




