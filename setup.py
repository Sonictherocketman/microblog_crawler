from distutils.core import setup

setup(
    name='MicroblogCrawler',
    version='1.1.6',
    author='Brian Schrader',
    author_email='brian@biteofanapple.com',
    packages=['microblogcrawler', 'test'],
    scripts=[], # TODO: Add bin/ scripts here.
    url='https://github.com/Sonictherocketman/microblog_feedcrawler',
    license='LICENSE.txt',
    description='A basic microblog/rss feed crawler modeled after the Tweepy StreamListener.',
    long_description=open('README.md').read(),
    install_requires=[
        'datetime',
        'python-dateutil',
        'requests',
        'lxml'
        ]
    )
