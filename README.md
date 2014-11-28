# Microblog Feed Crawler

Currently InDev!

A basic feed crawler/parser for traversing [microblog][1] and RSS feeds.  

[1]: http://openmicroblog.com

The crawler's API is modeled afer the [Tweepy][2] StreamListener API. To use the crawler, subclass it and fill in the methods for the `on_event` methods. 

[2]: https://github.com/tweepy/tweepy

The crawler provides very basic control over the crawling process. The crawler can be forced to start upon instantiation, or at a later time. The crawler also has an API for graceful termination and progress checking.

Upon instantiation, or when the `on_start` method is called, provide a list of feed URLs to crawl. The list can be modified either during instantiation, or during this callback.  The progress indicator will indicate the progress of the crawler through the list. When the crawler finishes the list, it will start over until the `stop` call is made. 

Providing a `start_time` to the crawler will cause the crawler to only callback to the `on_item` callback when an item has been found with a pubdate element value of that time or after. After the initial pass, the crawler will only callback to posts it has not seen before.

Providing the `deep_traversal` option will force the crawler to crawl all past pages of a given URL (if they exist). By default, the crawler will parse the first 2 pages of the given URL, but will stop after that.


