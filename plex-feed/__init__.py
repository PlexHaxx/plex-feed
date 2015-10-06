#!/usr/bin/env python3

import concurrent.futures

import pytz
from plexapi.myplex import MyPlexUser
from feedgen.feed import FeedGenerator


data = []


def parse_resource(user, resource):
    for section in user.getResource(resource.name).connect().library.sections():
        for video in section.recentlyAdded():
            if video.lastViewedAt:
                continue
            data.append(video)
    return True


def main():
    config = __import__('config')
    user = MyPlexUser.signin(config.username, config.password)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for resource in user.resources():
            executor.submit(parse_resource, user, resource)

    print('Servers data parsed')
    paris = pytz.timezone('Europe/Paris')
    ordered = reversed(sorted(data, key=lambda x: paris.localize(x.addedAt)))
    print('Media sorted')

    fg = FeedGenerator()
    fg.id('http://satreix.fr/feeds/plex.rss')
    fg.generator('plex-feed')
    fg.title('PLEX feed')
    fg.subtitle('Newly added media content')
    fg.author({'name': 'satreix', 'email': 'satreix@gmail.com'})
    fg.link(href='http://satreix.fr', rel='alternate')
    fg.logo('https://plex.tv/assets/img/googleplus-photo-cb6f717c8cfd8b48df6dbb09aa369198.png')
    fg.link(href='http://satreix.fr/feeds/plex.rss', rel='self')
    fg.language('en')

    for elt in list(ordered)[:50]:
        fe = fg.add_entry()
        fe.id(elt.getStreamUrl())
        fe.title('{} - {}'.format(elt.title, elt.server.friendlyName))
        fe.pubdate(paris.localize(elt.addedAt))
        fe.description(elt.summary, True)

    fg.rss_file('plex.rss', pretty=True)
    print('File written')


if __name__ == '__main__':
    main()
