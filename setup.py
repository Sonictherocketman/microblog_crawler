from setuptools import setup

setup(
    name='MicroblogCrawler',
    version='1.0.30',
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
        ]
    )
