"""Channel kit: logo (800x800), banner (2560x1440), watermark (150x150) into channel/.

    python3 scripts/make_kit.py
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from engine import brand as B  # noqa: E402
from engine.thumbs import world  # noqa: E402
from content.season import load_episode  # noqa: E402


def banner_scene():
    """A quiet rainy night with all the regulars and a well-filled wall: Episode 9, at closing."""
    tl = load_episode(9)
    t = [ln['t0'] for ln in tl.lines if ln['text'].startswith('Same time next rain')][0] + 0.5
    return world(tl, t)


def main(out=os.path.join(ROOT, 'channel')):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, im in (('logo_800.png', B.logo()), ('watermark_150.png', B.watermark()),
                     ('banner_2560x1440.png', B.banner(banner_scene()))):
        p = os.path.join(out, name)
        im.save(p, optimize=True)
        paths.append(p)
    print('\n'.join(paths))


if __name__ == '__main__':
    main(*sys.argv[1:])
