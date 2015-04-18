from setuptools import setup


setup(
    name='MicroblogCrawler',
    version='1.4',
    author='Brian Schrader',
    author_email='brian@biteofanapple.com',
    packages=['microblogcrawler', 'test'],
    scripts=[], # TODO: Add bin/ scripts here.
    url='https://github.com/Sonictherocketman/microblog_feedcrawler',
    license='LICENSE.txt',
    description='A basic microblog/rss feed crawler modeled after the Tweepy StreamListener.',
    keywords=['microblog', 'crawler', 'rss'],
    install_requires=[
        'datetime',
        'python-dateutil',
        'requests',
        'lxml'
        ],
    long_description='''A basic feed crawler/parser for traversing microblog and RSS feeds.

    The crawler's API is modeled afer the Tweepy StreamListener API. To use the crawler, subclass it and fill in the methods for the on_event methods. The crawler is meant to be quick and simple since it is designed to work close to real time. In later versions features may be added to address this directly (multiprocessing, simpler processing, etc).

    The crawler provides very basic control over the crawling process. The crawler can be forced to start upon instantiation, or at a later time. The crawler also has an API for graceful termination and progress checking.

    Upon instantiation, or when the on_start method is called, provide a list of feed URLs to crawl. The list can be modified either during instantiation, or during this callback. The progress indicator will indicate the progress of the crawler through the list. When the crawler finishes the list, it will start over until the stop call is made.

    Providing a start_time to the crawler will cause the crawler to only callback to the on_item callback when an item has been found with a pubdate element value of that time or later. Regardless of the given start_now value after the initial pass, the crawler will only callback to posts it has not seen before.

    Providing the deep_traversal option will force the crawler to crawl all past pages of a given URL (if they exist). By default, the crawler will parse the first 2 pages of the given URL every time, but will stop after that.

    The crawler returns Python dictionary representations of the element objects it finds in almost every callback excluding the on_data callback which recieves the raw text of the URL response. In cases where the crawler encounters an error, the crawler will pass a dictionary with the following structure to the on_error callback.'''
    )
