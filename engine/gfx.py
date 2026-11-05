"""Palette, drawing helpers and fonts shared by every part of the renderer.

The world is drawn at 320x180 ("scene pixels"); text and cards at 640x360 (landscape)
or 360x640 (vertical Shorts); ffmpeg scales the result x3 with nearest neighbour.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 320, 180
FPS = 30

_FONT_PATHS = [
    os.environ.get('TSR_FONT', ''),
    os.path.join(os.path.dirname(__file__), '..', 'fonts', 'unifont_jp.otf'),
    '/usr/share/fonts/opentype/unifont/unifont_jp.otf',
    '/usr/share/fonts/truetype/unifont/unifont_jp.ttf',
]


def _font():
    for p in _FONT_PATHS:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, 16)
    raise SystemExit('GNU Unifont (unifont_jp.otf) not found: apt-get install fonts-unifont')


FONT = _font()

C = dict(
    O=(36, 26, 34), ceiling=(30, 21, 22), beam=(66, 42, 32), beam_hi=(100, 66, 46),
    wall=(190, 156, 116), wall_dk=(168, 134, 98), wall_hi=(206, 174, 134),
    post=(94, 60, 40), post_hi=(126, 84, 56),
    wood=(136, 88, 54), wood_dk=(100, 64, 40), wood_hi=(170, 116, 72), wood_top=(200, 150, 96),
    floor=(88, 58, 42), floor_dk=(70, 46, 34), floor_ln=(54, 36, 28),
    indigo=(48, 60, 108), indigo_hi=(72, 88, 144), indigo_dk=(32, 40, 78),
    red=(188, 58, 46), red_dk=(136, 38, 34), red_hi=(226, 100, 76),
    metal=(156, 156, 164), metal_dk=(102, 102, 114), metal_hi=(208, 208, 214),
    white=(240, 236, 226), cream=(232, 218, 186), tile=(222, 220, 208), tile_ln=(184, 182, 172),
    skin=(242, 202, 166), skin_dk=(214, 166, 134), blush=(236, 140, 126),
    hair=(58, 40, 38), mouth=(150, 62, 56), dark=(40, 30, 34),
    fur=(232, 134, 58), fur_dk=(188, 96, 42), fur_lt=(250, 222, 182), tip=(74, 48, 40),
    haori=(60, 96, 72), haori_dk=(42, 70, 54),
    bowl=(234, 230, 218), bowl_dk=(196, 190, 178), tofu=(214, 150, 70), tofu_dk=(170, 106, 44),
    nori=(40, 62, 46), chashu=(196, 120, 96), egg=(244, 240, 226), yolk=(240, 164, 60),
    naruto=(240, 234, 230), pink=(226, 120, 140), onion=(120, 178, 82), cucumber=(96, 160, 72),
    paper=(246, 228, 178), paper_dk=(216, 186, 130), lacquer=(44, 32, 32),
    gold=(222, 178, 86), gold_dk=(168, 124, 52),
)

SEATS = [124, 156, 188, 220, 252, 284]       # stool x positions, seat 1..6
POT_X = 281
DOOR_IN = (30, 146)                          # where a walker steps through the door
FLOOR_Y = 170                                # walking line in front of the stools


def seat_x(n):
    return SEATS[int(n) - 1]


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def ease(u):
    u = clamp(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def mix(c1, c2, k):
    return tuple(int(round(a + (b - a) * k)) for a, b in zip(c1, c2))


def shade(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c)


# ---------------------------------------------------------------- primitives
def R(d, x0, y0, x1, y1, c):
    d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=c)


def E(d, x0, y0, x1, y1, c):
    d.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=c)


def PG(d, pts, c):
    d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=c)


def PX(d, x, y, c):
    d.point((int(round(x)), int(round(y))), fill=c)


def LN(d, pts, c, w=1):
    d.line([(int(round(x)), int(round(y))) for x, y in pts], fill=c, width=w)


class Pen:
    """Draw in local coordinates mirrored by facing f (+1 right, -1 left) around cx."""

    def __init__(self, d, cx, f=1):
        self.d, self.cx, self.f = d, cx, f

    def X(self, dx):
        return self.cx + self.f * dx

    def rect(self, dx0, y0, dx1, y1, c):
        R(self.d, self.X(dx0), y0, self.X(dx1), y1, c)

    def ell(self, dx0, y0, dx1, y1, c):
        E(self.d, self.X(dx0), y0, self.X(dx1), y1, c)

    def poly(self, pts, c):
        PG(self.d, [(self.X(x), y) for x, y in pts], c)

    def px(self, dx, y, c):
        PX(self.d, self.X(dx), y, c)

    def line(self, pts, c, w=1):
        LN(self.d, [(self.X(x), y) for x, y in pts], c, w)


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        u = i / (n - 1)
        a, b, c_, e = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c_ * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c_ * p2[1] + e * p3[1]))
    return out


def outline(layer, color=C['O']):
    """1px outline around everything opaque in an RGBA layer."""
    a = np.asarray(layer)
    m = a[:, :, 3] > 0
    dil = m.copy()
    dil[1:] |= m[:-1]
    dil[:-1] |= m[1:]
    dil[:, 1:] |= m[:, :-1]
    dil[:, :-1] |= m[:, 1:]
    edge = dil & ~m
    out = a.copy()
    out[edge] = (*color, 255)
    return Image.fromarray(out, 'RGBA')


def new_layer(w=W, h=H):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def glyph_mask(ch, size=16):
    """Unifont glyph as a boolean array (16 rows)."""
    g = Image.new('L', (32, 18), 0)
    ImageDraw.Draw(g).text((0, -1), ch, font=FONT, fill=255)
    a = np.asarray(g) > 0
    cols = np.nonzero(a.any(0))[0]
    if len(cols) == 0:
        return a[:, :8]
    return a[:, :max(8, cols.max() + 1)]


def text_w(s):
    return int(FONT.getlength(s))


def wrap(s, maxw):
    """Word wrap for Latin text; CJK runs may break anywhere."""
    out, cur = [], ''
    for para in s.split('\n'):
        words = para.split(' ')
        cur = ''
        for w_ in words:
            cand = (cur + ' ' + w_).strip() if cur else w_
            if text_w(cand) <= maxw:
                cur = cand
                continue
            if cur:
                out.append(cur)
            cur = w_
            while text_w(cur) > maxw:          # very long token (Japanese): hard break
                k = len(cur)
                while k > 1 and text_w(cur[:k]) > maxw:
                    k -= 1
                out.append(cur[:k])
                cur = cur[k:]
        out.append(cur)
    return out


def text_img(s, color, shadow=None, scale=1):
    w = text_w(s) + 4
    im = Image.new('RGBA', (w, 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    if shadow:
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            d.text((2 + ox, 1 + oy), s, font=FONT, fill=shadow)
    d.text((2, 1), s, font=FONT, fill=color)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return im
