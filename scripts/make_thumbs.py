"""Thumbnails: A and B (1280x720) for episodes, one for the trailer, and a vertical one
(1080x1920) for each Short.

    python3 scripts/make_thumbs.py --out out ep01 short05 trailer
    python3 scripts/make_thumbs.py --out out thumbs-week-2      # the Shorts of one week
    python3 scripts/make_thumbs.py --out out all
Items that have no thumbnail are skipped quietly, so the render workflow can call this for every item.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from engine import thumbs as T  # noqa: E402
from content import meta as M  # noqa: E402
from content.season import load_episode  # noqa: E402
from content import shorts as SH  # noqa: E402
from content.cast import CAST  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def episode(n, out):
    tl = load_episode(n)
    who, words = M.THUMBS[n]
    paths = []
    for tag, im in (('A', T.thumb_a(tl, who, words, n)), ('B', T.thumb_b(tl, who))):
        p = os.path.join(out, f'timeslip-ramen-ep{n:02d}-thumb-{tag}.png')
        im.save(p, optimize=True)
        paths.append(p)
    return paths


def short(n, out):
    sh = SH.by_number(n)
    tl = load_episode(sh['ep'])
    c = CAST[sh['who']]
    im, _ = T.thumb_short(tl, sh['who'], tl.short_windows(n), sh['hook'], c['name_jp'], c['name'], sh.get('cam'))
    p = os.path.join(out, f'timeslip-ramen-short{n:02d}-thumb.png')
    im.save(p, optimize=True)
    return [p]


def week_shorts(week):
    with open(os.path.join(ROOT, 'docs', 'upload-schedule.json'), encoding='utf-8') as f:
        return [i['id'] for i in json.load(f) if i['kind'] == 'short' and i['release'] == week]


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
        if it == 'all':
            items += [f'ep{n:02d}' for n in range(1, 13)] + ['trailer'] + [f'short{n:02d}' for n in range(1, 29)]
        elif it.startswith('thumbs-week-'):
            items += week_shorts(it[len('thumbs-'):])
        else:
            items.append(it)
    for it in items:
        if it.startswith('ep'):
            print('\n'.join(episode(int(it[2:]), a.out)))
        elif it.startswith('short'):
            print('\n'.join(short(int(it[5:]), a.out)))
        elif it == 'trailer':
            print('\n'.join(trailer(a.out)))


if __name__ == '__main__':
    main()
