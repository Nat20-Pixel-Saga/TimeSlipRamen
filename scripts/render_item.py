"""Render one item: ep01..ep12, short01..short28, trailer.

    python3 scripts/render_item.py ep01 --out out --workers 4
    python3 scripts/render_item.py short05 --out out
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from engine.render import render  # noqa: E402
from engine.audio import track_length  # noqa: E402
from content.season import load_episode  # noqa: E402
from content.words import WORDS  # noqa: E402
from content.facts import FACTS  # noqa: E402
from content import shorts as SH  # noqa: E402


def episode(n, out, workers, limit=None):
    tl = load_episode(n)
    plan = []
    tr = tl.teaser_range()
    if tr:
        plan.append(tr)
    end = tl.duration if limit is None else min(tl.duration, limit)
    plan.append((0.0, end))
    at = (tr[1] - tr[0]) if tr else 0.0
    path = os.path.join(out, f'timeslip-ramen-ep{n:02d}.mp4')
    render(tl, path, 'landscape', WORDS, FACTS, plan, tl.meta['music'], music_at=at, workers=workers,
           target_lufs=-16, seed=n)
    return path


def short(n, out, workers):
    sh = SH.by_number(n)
    tl = load_episode(sh['ep'])
    plan = tl.short_windows(n)
    st = tl._state_of(sh['who'], plan[0][0] + 0.01)
    cam = sh.get('cam') or (st['x'] if st else 220)
    music = [sh.get('music') or tl.meta['music'][0]]
    start = (n * 37) % max(10, int(track_length(music[0]) - 70))
    path = os.path.join(out, f'timeslip-ramen-short{n:02d}.mp4')
    render(tl, path, 'short', WORDS, FACTS, plan, music, music_start=start, music_at=0.0, hook=sh['hook'], cam=cam,
           subject=sh['who'], workers=workers, target_lufs=-15, seed=100 + n)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('item')
    ap.add_argument('--out', default='out')
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--limit', type=float, default=None, help='episodes: stop after this many seconds (tests)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    it = a.item
    if it.startswith('thumbs-'):
        print('thumbnails only: scripts/make_thumbs.py renders them')
    elif it.startswith('ep'):
        print(episode(int(it[2:]), a.out, a.workers, a.limit))
    elif it.startswith('short'):
        print(short(int(it[5:]), a.out, a.workers))
    elif it == 'trailer':
        from content.trailer import render_trailer
        print(render_trailer(a.out, a.workers))
    else:
        raise SystemExit(f'unknown item {it}')


if __name__ == '__main__':
    main()
