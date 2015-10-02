#!/usr/bin/env python3

import sys
import bisect

from plexapi.myplex import MyPlexUser
from clint.textui import colored


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
                d = MyResource(video.title, resource.name, section.title,
                               resource.createdAt)
                bisect.insort(data, d)
                print(colored.green('.'), end='')
                sys.stdout.flush()
        print()

    for elt in reversed(data):
        pass
        #print('- {} {}'.format(elt.date, elt.title))

    print(len(data))