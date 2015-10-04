#!/usr/bin/env python3

import sys
import bisect
import datetime

import pytz
from plexapi.myplex import MyPlexUser
from clint.textui import colored
from feedgen.feed import FeedGenerator


class MyResource:
    def __init__(self, title, server, section, date):
        self.title = title
        self.server = server
        self.section = section
        self.date = date

    def __lt__(self, other):
        return self.date < other.date


def main():
    data = []
    config = __import__('config')
    user = MyPlexUser.signin(config.username, config.password)

    for resource in user.resources():
        plex = user.getResource(resource.name).connect()

        for section in plex.library.sections():
            for video in section.recentlyAdded():
                if video.lastViewedAt:
                    print(colored.red('X'), end='')
                    sys.stdout.flush()
                    continue

                d = MyResource(
                    video.title, resource.name, section.title,
                    pytz.timezone('Europe/Paris').localize(resource.createdAt)
                )
                bisect.insort(data, d)
                print(colored.green('.'), end='')
                sys.stdout.flush()
        print()

    ordered = reversed(data)
    print(len(data))

    fg = FeedGenerator()
    fg.id('http://satreix.fr/feeds/plex.rss')
    fg.title('PLEX feed')
    fg.author({'name': 'satreix', 'email': 'satreix@gmail.com'})
    fg.link(href='http://satreix.fr', rel='alternate')
    fg.logo('https://plex.tv/assets/img/googleplus-photo-cb6f717c8cfd8b48df6dbb09aa369198.png')
    fg.subtitle('Newly added media content')
    fg.link(href='http://satreix.fr/feeds/plex.rss', rel='self')
    fg.language('en')

    for elt in ordered:
        # print('- {} {}'.format(elt.date, elt.title))
        fe = fg.add_entry()
        # fe.id('http://lernfunk.de/media/654321/1')
        fe.title(elt.title)
        fe.pubdate(elt.date)
        # fe.description(elt.server)
        # fe.category(elt.section)

    fg.rss_file('plex.rss')
    print('File wrote')


if __name__ == '__main__':
    main()
