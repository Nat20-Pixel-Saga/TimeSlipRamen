"""Thumbnails A and B (1280x720) for episodes and the trailer.

    python3 scripts/make_thumbs.py --out out ep01 ep02 trailer
    python3 scripts/make_thumbs.py --out out all
Items that have no thumbnail (Shorts, channel-kit) are skipped quietly, so the render workflow can
call this for every item.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from engine import thumbs as T  # noqa: E402
from content import meta as M  # noqa: E402
from content.season import load_episode  # noqa: E402


def episode(n, out):
    tl = load_episode(n)
    who, words = M.THUMBS[n]
    paths = []
    for tag, im in (('A', T.thumb_a(tl, who, words, n)), ('B', T.thumb_b(tl, who))):
        p = os.path.join(out, f'timeslip-ramen-ep{n:02d}-thumb-{tag}.png')
        im.save(p, optimize=True)
        paths.append(p)
    return paths


def trailer(out):
    tl = load_episode(12)
    t = next(c['t0'] for c in tl.cards if c['id'] == 'tanjoubi') + 1.0
    im = T.thumb_wide(tl, t, ('OPEN TO', 'EVERY CENTURY'))
    p = os.path.join(out, 'timeslip-ramen-trailer-thumb-A.png')
    im.save(p, optimize=True)
    return [p]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('items', nargs='+')
    ap.add_argument('--out', default='out')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    items = []
    for it in a.items:
        items += [f'ep{n:02d}' for n in range(1, 13)] + ['trailer'] if it == 'all' else [it]
    for it in items:
        if it.startswith('ep'):
            print('\n'.join(episode(int(it[2:]), a.out)))
        elif it == 'trailer':
            print('\n'.join(trailer(a.out)))


if __name__ == '__main__':
    main()
