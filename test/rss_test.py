""" Tests for the crawler module. Includes a basic subclass for testing use. """

import unittest, os, sys, time, signal
sys.path.insert(0, '../')
from microblogcrawler.crawler import FeedCrawler


class MyFeedCrawler(FeedCrawler):
    """ A basic testing class implementation. """

    def __init__(self, links, start_now=False):
        self.total_time = 0
        self.count = 0
        FeedCrawler.__init__(self, links, start_now=start_now)

    def on_start(self):
        self.count = 0
        self.total_time = time.time()

    def on_finish(self):
        print '{0} New Items | {1} seconds'.format(self.count, time.time() - self.total_time)

    def on_info(self, link, info):
        #print info
        pass

    def on_item(self, link, info, item):
        self.count += 1
        #print 'Item text: {0}\n{1}'.format(info, item)
        pass

    def on_error(self, link, error):
        print 'Error for {}:\n {}'.format(link, error['description'])
        pass

# TODO Add more feeds, and some microblog feeds.
links = [
        # RSS Feeds
        'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml',
        'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'http://www.marco.org/rss',
        'http://daringfireball.net/feeds/',
        'http://inessential.com/xml/rss.xml',
        'http://brianschrader.com/rss',
        'http://david-smith.org/atom.xml',
        'http://globalspin.com/feed',
        'http://rss.feedsportal.com/c/270/f/3547/index.rss',
        'http://feeds.nytimes.com/nyt/rss/Technology',
        'http://hosted.ap.org/lineups/SCIENCEHEADS-rss_2.0.xml?SITE=OHLIM&SECTION=HOME',
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://feeds.nytimes.com/nyt/rss/HomePage',
        'http://rssfeeds.usatoday.com/usatoday-NewsTopStories',
        'http://www.npr.org/rss/rss.php?id=1001',
        'http://newsrss.bbc.co.uk/rss/newsonline_world_edition/americas/rss.xml',
        'http://www.pbs.org/wgbh/pages/frontline/rss/files.xml',
        'http://www.pbs.org/wgbh/nova/rss/nova.xml',
        'http://www.loc.gov/rss/read/eca.xml',
        'http://dictionary.reference.com/wordoftheday/wotd.rss',
        'http://feeds.feedburner.com/time/photoessays',
        'http://hosted.ap.org/lineups/SPORTSHEADS-rss_2.0.xml?SITE=VABRM&SECTION=HOME',
        'http://rss.cnn.com/rss/si_topstories.rss',
        'http://feeds1.nytimes.com/nyt/rss/Sports',
        'http://sports.yahoo.com/top/rss.xml',
        'http://www.nba.com/jazz/rss.xml',
        'http://www.npr.org/rss/rss.php?id=1008',
        'http://www.newyorker.com/feed/humor',
        'http://www.npr.org/rss/rss.php?id=13',
        'http://www.npr.org/rss/rss.php?id=1045',
        'http://www.nationalgeographic.com/adventure/nga.xml',
        'http://feeds.reuters.com/reuters/topNews',

        # THESE TESTING FEEDS CAUSE PROBLEMS
        # TODO: Investigate why. These feeds are never marked as read and items
        # reappear every iteration.
        #'http://newsrss.bbc.co.uk/rss/newsonline_world_edition/americas/rss.xml',
        #'http://feeds.reuters.com/reuters/topNews',
        #'http://www.npr.org/rss/rss.php?id=1001',

        # Microblog feeds
        'http://microblog.brianschrader.com/feed'
        ]
crawler = MyFeedCrawler(links)

def signal_handler(signal, frame):
    crawler.stop()
signal.signal(signal.SIGINT, signal_handler)

crawler.start()
