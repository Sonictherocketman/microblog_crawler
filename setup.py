from setuptools import setup
import os

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='microblogcrawler',
    version='1.0.2',
    author='Brian Schrader',
    author_email='brian@biteofanapple.com',
    packages=['microblogcrawler', 'test'],
    scripts=[], # TODO: Add bin/ scripts here.
    url='https://github.com/Sonictherocketman/microblog_feedcrawler',
    license='LICENSE.txt',
    description='A basic microblog/rss feed crawler modeled after the Tweepy StreamListener.',
    long_description=read('README.md'),
    install_requires=[
        'datetime',
        'dateutil',
        'requests',
        'lxml'
        ]
    )
