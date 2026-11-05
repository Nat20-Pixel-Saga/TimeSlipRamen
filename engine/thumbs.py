"""YouTube thumbnails, 1280x720, for the A/B test (YouTube Studio > Test & compare).

A: the visitor stepping through the door with their century behind them, the regulars at the
   counter, and two lines of big hook words.  Everything is drawn on one pixel grid (x6).
B: the whole shop, warm and steaming, with nobody saying anything: no words at all (x4).
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .gfx import FONT, text_w
from .shop import Shop

INK = (26, 18, 32)
CREAM = (252, 240, 214)
GOLD = (255, 196, 92)
RED = (196, 52, 40)


def world(tl, t, extra_lights=(), hide=()):
    st = tl.state(t)
    st['lights'] = list(st.get('lights', [])) + list(extra_lights)
    st['chars'] = [c for c in st['chars'] if c.get('who') not in hide]
    st.pop('establish', None)
    w = Shop(tl.cast).render(st, t)
    return Image.fromarray((w * 255 + 0.5).astype(np.uint8))


def door_time(tl, who, x_at=36):
    """First moment the visitor is just inside the door, so their world shows behind them."""
    segs = tl.segs.get(who, [])
    if not segs:
        raise KeyError(who)
    t = segs[0][0]
    while t < segs[0][0] + 40:
        x = tl._xof(who, t)
        if x is not None and x >= x_at:
            return t
        t += 1 / 30
    return segs[0][0] + 1


def cozy_time(tl, who):
    """A moment with the visitor seated and their bowl steaming."""
    lines = [ln for ln in tl.lines if ln['who'] == who]
    t = lines[0]['t0'] if lines else tl.segs[who][0][0] + 6
    end = t + 90
    while t < end:
        x = tl._xof(who, t)
        st = tl.state(t)
        if x is not None and any(abs(b['x'] - x) < 22 and b.get('steam', 0) > 0 and not b.get('floor')
                                 for b in st['bowls']):
            return t + 2.0
        t += 0.5
    return lines[0]['t0'] + 3 if lines else t


def big_words(lines, colors, scale=8, width=1280, height=720, right=24, top=22, gap=4):
    """Big bold pixel words: Unifont doubled for weight, a 1 px ink outline and a 1 px shadow,
    all drawn at 1x and blown up by `scale` (one font pixel = `scale` screen pixels)."""
    im = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    y = top
    for s, col in zip(lines, colors):
        tw = text_w(s) + 1
        m = Image.new('L', (tw + 6, 21), 0)
        d = ImageDraw.Draw(m)
        d.fontmode = '1'
        d.text((3, 2), s, font=FONT, fill=255)
        d.text((4, 2), s, font=FONT, fill=255)
        out = m.filter(ImageFilter.MaxFilter(3))
        lay = Image.new('RGBA', (m.width + 1, m.height + 1), (0, 0, 0, 0))
        lay.paste(Image.new('RGBA', m.size, INK + (140,)), (1, 1), out)
        lay.paste(Image.new('RGBA', m.size, INK + (255,)), (0, 0), out)
        lay.paste(Image.new('RGBA', m.size, col + (255,)), (0, 0), m)
        lay = lay.resize((lay.width * scale, lay.height * scale), Image.NEAREST)
        im.alpha_composite(lay, (width - right - lay.width + 3 * scale, y))
        y += 17 * scale + gap
    return im


def ep_tag(n):
    s = f'EP{n}'
    tw = text_w(s)
    im = Image.new('RGBA', (tw + 8, 19), RED + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, im.width - 1, im.height - 1), outline=INK)
    d.rectangle((1, 1, im.width - 2, im.height - 2), outline=(232, 110, 90))
    d.fontmode = '1'
    d.text((4, 1), s, font=FONT, fill=CREAM)
    return im


def shade_top(im, rows, k=0.62):
    a = np.asarray(im).astype(np.float32)
    for y in range(min(rows, a.shape[0])):
        f = 1 - k * (1 - y / rows) ** 1.4
        a[y] *= f
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def thumb_a(tl, who, words, n, colors=(CREAM, GOLD)):
    t = door_time(tl, who)
    x = tl._xof(who, t)
    base = world(tl, t, extra_lights=[(x, 128, 46, (1.0, 0.8, 0.55), 0.7)], hide=('kasa',))
    crop = shade_top(base.crop((0, 60, 214, 180)), 52, 0.7).convert('RGBA')
    tag = ep_tag(n)
    crop.alpha_composite(tag, (crop.width - tag.width - 5, crop.height - tag.height - 5))
    big = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST).crop((0, 0, 1280, 720))
    big.alpha_composite(big_words(words, colors))
    return big.convert('RGB')


def thumb_b(tl, who):
    t = cozy_time(tl, who)
    base = world(tl, t)
    return base.resize((1280, 720), Image.NEAREST)


def thumb_wide(tl, t, words, colors=(CREAM, GOLD)):
    """Trailer: the whole shop at x4 with two lines of words."""
    base = shade_top(world(tl, t), 70, 0.7).resize((1280, 720), Image.NEAREST).convert('RGBA')
    base.alpha_composite(big_words(words, colors, scale=7))
    return base.convert('RGB')
