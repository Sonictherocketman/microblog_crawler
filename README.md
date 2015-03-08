# Microblog Feed Crawler

*Version 1.3!*

A basic feed crawler/parser for traversing [microblog][1] and RSS feeds.  

[1]: http://openmicroblog.com

The crawler's API is modeled afer the [Tweepy][2] StreamListener API. To use the crawler, subclass it and fill in the `on_event` methods. The crawler is meant to be quick and simple. In later versions features may be added to increase the performance (multiprocessing, simpler processing, etc). 

[2]: https://github.com/tweepy/tweepy

The crawler provides a few basic controls for starting, stopping, and monitering its progress. The crawler can be forced to start upon instantiation, or at a later time. The crawler also has an API for graceful termination and progress checking.

Upon instantiation, or when the `on_start` method is called, provide a list of feed URLs to crawl. The list can be modified either during instantiation, or during this callback.  The progress indicator will indicate the progress of the crawler through the list. When the crawler finishes the list, it will start over until the `stop` call is made. 

Providing a `start_time` to the crawler will cause the crawler to only callback to the `on_item` callback when an item has been found with a pubdate element value of that time or later. Regardless of the given `start_now` value after the initial pass, the crawler will only callback to posts it has not seen before.

Providing the `deep_traversal` option will force the crawler to crawl all past pages of a given URL (if they exist). By default, the crawler will parse the first 2 pages of the given URL every time, but will stop after that.

The crawler returns Python dictionary representations of the element objects it finds in almost every callback excluding the `on_data` callback which recieves the raw text of the URL response. In cases where the crawler encounters an error, the crawler will pass a dictionary with the following structure to the `on_error` callback.

<pre><code>
error = {
    'code': The error code of the HTTP response (in most cases). 
        If the error is not an HTTP error and is instead due to 
        a parsing error, then the code will be -1.
    'description': A brief description of what went wrong.
    }
</code></pre>

## Installation

`pip install MicroblogCrawler`

## Version Notes

Version 1.3 is now multiprocessed! 

----

Among other things, version 1.3 also includes a number of fixes and improvements.

- `on_item` callback now includes the feed information as the second parameter. This is a breaking change in the API.
- `on_info` callback now recieves a dictionary response of all of the info fields in a given feed. Previous versions recieved a name, value tuple.
- Multiprocessing now allows the crawler to process 4 feeds (or more if you override the value) at once. 
- Fixed a number of bugs that allowed duplicates. 
- Fixed an issue where feed crawl times may be inaccurately reported.
- Fixed the timezone problem. Feeds without timezones are parsed according to their HTTP response timezone.

Added a bunch of 'Good Citizen' features like:
- Added crawler user agent and proper subscriber count reporting to remote servers.
- Crawler is now HTTP status code aware and static files will not be parsed if they have not been modified (HTTP 304).

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
    'http://example5.com/rss'
    ]
    crawler = MyFeedCrawler(links=links, start_now=True)

</code></pre>

## Future Enhancements

- Add more tests and examples.
- Handle Unicode more gracefully. Currently, the parser basically ignores Unicode and tries to hand all the work off to `lxml`. The type of data that the callbacks recieve is therefore not consistent.

## Performance

Although the crawler hasn't gone through formal testing, The results of limited tests are below:

<table>
    <thead>
        <tr>
            <td>Number of Feeds</td>
            <td>Average Crawl Time</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>36</td>
            <td>1.763 (s)</td>
        </tr>
    </tbody>
</table>

## Acknowlegements

The microblogcrawler module makes heavy use of, and requires the following 3rd party modules.

- `lxml` for all the feed parsing.
- `requests` for HTTP requests.
- `datetime` for obvious reasons.
- `dateutil` for parsing and interpretting varying datetime string formats.

My thanks to all of the developers who made this project possble.
