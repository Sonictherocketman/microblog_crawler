# Microblog Feed Crawler

*Version 1.0!*

A basic feed crawler/parser for traversing [microblog][1] and RSS feeds.  

[1]: http://openmicroblog.com

The crawler's API is modeled afer the [Tweepy][2] StreamListener API. To use the crawler, subclass it and fill in the methods for the `on_event` methods. The crawler is meant to be quick and simple since it is designed to work close to real time. In later versions features may be added to address this directly (multiprocessing, simpler processing, etc). 

[2]: https://github.com/tweepy/tweepy

The crawler provides very basic control over the crawling process. The crawler can be forced to start upon instantiation, or at a later time. The crawler also has an API for graceful termination and progress checking.

Upon instantiation, or when the `on_start` method is called, provide a list of feed URLs to crawl. The list can be modified either during instantiation, or during this callback.  The progress indicator will indicate the progress of the crawler through the list. When the crawler finishes the list, it will start over until the `stop` call is made. 

Providing a `start_time` to the crawler will cause the crawler to only callback to the `on_item` callback when an item has been found with a pubdate element value of that time or after. After the initial pass, the crawler will only callback to posts it has not seen before.

Providing the `deep_traversal` option will force the crawler to crawl all past pages of a given URL (if they exist). By default, the crawler will parse the first 2 pages of the given URL, but will stop after that.

The crawler returns Python dictionary representations of the element objects it finds in almost every callback excluding the `on_data` callback which recieves the raw text of the URL response. In cases where the crawler encounters an error, the crawler will pass a dictionary with the following structure to the `on_error` callback.

<pre><code>
error = {
    'link': The URL of the feed that caused the error,
    'code': The error code of the HTTP response (in most cases). 
        If the error is not an HTTP error and is instead due to 
        a parsing error, then the code will be -1.
    'description': A brief description of what went wrong.
    }
</code></pre>

## Version Notes

- *Important:* At version 1.0, the crawler has yet to be tested with any medium-large number (100+) of feeds to crawl. Since the crawler is designed to handle large numbers of feeds quickly, this will be a huge concern in coming versions.  

## Usage

For a sample use case, check out the test module. For basic usage, see below.

<pre><code>
from microblogcrawler.crawler import FeedCrawler

class MyFeedCrawler(FeedCrawler):
    
    on_item(self, item):
        # Do something with the item.
        print item

if __name__ == '__main__':
    links = [
    'http://example1.com/rss',
    'http://example2.com/rss',
    'http://example3.com/rss',
    'http://example4.com/rss',
    'http://example5.com/rss',
    ]
    crawler = MyFeedCrawler(links=links, start_now=True)

</code></pre>
## Bugs

- Callbacks (except the `on_data` callback) may recieve either Unicode, or Python ASCII Strings as data. As of yet the results are inconsistant. 
- Due to the large potential processing overhead required to convert an entire RSS or Microblog feed into an lxml etree, the callback for `on_feed` is currently disabled. This feature may be reenabled in future versions but will require the explicit options to enable and will be disabled by default.

## Future Enhancements

- Add a backup feed parser for when `lxml` fails due to malformed XML (maybe Beautiful Soup).
- Increase the performance of the feed parser using the `multiprocessing` module. Currently, the parser only does requests in order. There's no reason that the crawler couldn't perform multiple requests and process them at once.
- Add more tests and examples.
- Handle Unicode more gracefully. Currently, the parser basically ignores Unicode and tries to hand all the work off to `lxml`. They type of data that the callbacks recieve is not consistent.
