"""Characters: a parametric person (seated from behind, profile heads, walking from the side),
animal folk (fox, tanuki, kappa, raijin, the grandmother fox) and a few one-off creatures
(dog, inch-high boy, umbrella yokai, dream eater, child spirit).

Every draw function paints onto an ImageDraw for a transparent 320x180 layer; the shop
outlines the layer afterwards.  Coordinates follow the shop: stools at SEATS, cushions at
y 133-140, the walking line at y 170 (feet), heads of seated customers at y 97.
"""
import math

from .gfx import C, R, E, PG, PX, LN, Pen, bez, clamp, mix, shade

SKIN = (242, 202, 166)
SKIN_DK = (214, 166, 134)
SHAVED = (214, 196, 182)
HAIR = (44, 34, 36)
GREY = (170, 164, 160)
WHITE_HAIR = (232, 230, 224)


class Look(dict):
    """A character's appearance; missing keys fall back to sensible defaults."""

    def __getattr__(self, k):
        return self.get(k)


def L(**kw):
    base = dict(kind='human', skin=SKIN, skin_dk=SKIN_DK, hair='short', hair_c=HAIR, hat=None, hat_c=(60, 40, 30),
                body='kimono', c1=(90, 80, 110), c2=None, collar=(232, 222, 200), sash=(150, 60, 50),
                beard=None, beard_c=None, glasses=False, prop=None, size=1.0, bow_obi=False, crest=None,
                layers=None, voice=1.0)
    base.update(kw)
    if base['c2'] is None:
        base['c2'] = shade(base['c1'], 0.72)
    if base['beard_c'] is None:
        base['beard_c'] = base['hair_c']
    return Look(base)


# ============================================================================ heads
def head_back(d, hx, hy, k):
    """Back of the head (the customer faces the counter)."""
    hs, hc = k.hair, k.hair_c
    if k.kind == 'kappa':
        E(d, hx - 6, hy, hx + 6, hy + 14, k.skin)
        E(d, hx - 7, hy + 1, hx + 7, hy + 9, (52, 92, 56))          # fringe
        E(d, hx - 5, hy - 1, hx + 5, hy + 4, (226, 222, 196))       # the dish
        if not k.get('spilled'):
            E(d, hx - 3, hy, hx + 3, hy + 3, (110, 170, 220))
        return
    R(d, hx - 2, hy + 12, hx + 1, hy + 16, k.skin_dk)
    if hs == 'bald':
        E(d, hx - 6, hy, hx + 6, hy + 14, k.skin)
        R(d, hx - 6, hy + 7, hx + 6, hy + 11, hc)
        E(d, hx - 4, hy + 1, hx - 1, hy + 4, mix(k.skin, (255, 255, 255), 0.35))
    elif hs in ('chonmage', 'topknot_band'):
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        E(d, hx - 4, hy, hx + 4, hy + 5, SHAVED)
        R(d, hx - 1, hy - 3, hx + 1, hy + 3, hc)
        if hs == 'topknot_band':
            R(d, hx - 6, hy + 5, hx + 6, hy + 6, (236, 232, 220))
            R(d, hx + 5, hy + 6, hx + 7, hy + 9, (236, 232, 220))
    elif hs == 'wild':
        E(d, hx - 7, hy - 1, hx + 7, hy + 14, hc)
        for sx_, sy_ in ((-8, 4), (8, 5), (-6, -2), (6, -2), (-8, 10), (8, 11)):
            PG(d, [(hx + sx_, hy + sy_), (hx + sx_ * 0.6, hy + sy_ + 3), (hx + sx_ * 0.6, hy + sy_ - 2)], hc)
        R(d, hx - 1, hy + 3, hx + 1, hy + 4, (190, 60, 50))
        PG(d, [(hx - 1, hy + 2), (hx + 2, hy - 5), (hx + 4, hy - 4), (hx + 1, hy + 3)], hc)
    elif hs in ('long', 'heian'):
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        end = 136 if hs == 'heian' else 128
        PG(d, [(hx - 6, hy + 8), (hx + 6, hy + 8), (hx + 5, end), (hx - 5, end)], hc)
        R(d, hx - 2, hy + 18, hx + 1, hy + 19, (236, 232, 220))
        PX(d, hx + 2, hy + 3, mix(hc, (255, 255, 255), 0.25))
    elif hs == 'bun':
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        E(d, hx - 4, hy + 4, hx + 4, hy + 11, shade(hc, 0.8))
        PX(d, hx - 2, hy + 6, mix(hc, (255, 255, 255), 0.3))
    elif hs == 'ponytail':
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        R(d, hx - 1, hy + 4, hx + 1, hy + 5, k.get('tie_c', (200, 60, 60)))
        PG(d, [(hx - 2, hy + 5), (hx + 2, hy + 5), (hx + 3, hy + 15), (hx, hy + 20), (hx - 2, hy + 14)], hc)
    elif hs == 'bob':
        E(d, hx - 7, hy - 1, hx + 7, hy + 13, hc)
        R(d, hx - 7, hy + 6, hx + 7, hy + 13, hc)
    elif hs == 'okuni':
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        R(d, hx - 1, hy + 2, hx + 1, hy + 3, (230, 200, 60))
        PG(d, [(hx - 1, hy + 2), (hx + 2, hy + 2), (hx + 4, hy + 18), (hx + 1, hy + 24), (hx - 2, hy + 16)], hc)
    elif hs == 'hood':
        E(d, hx - 6, hy, hx + 6, hy + 14, k.hat_c)
        R(d, hx - 5, hy + 7, hx + 5, hy + 7, shade(k.hat_c, 0.75))
        R(d, hx - 3, hy + 12, hx + 2, hy + 14, k.skin_dk)
    elif hs == 'horns':
        E(d, hx - 7, hy - 1, hx + 7, hy + 14, hc)
        for s in (-1, 1):
            PG(d, [(hx + s * 3, hy + 1), (hx + s * 6, hy - 6), (hx + s * 5, hy + 1)], (236, 220, 180))
        for s in (-9, -6, 6, 9):
            PG(d, [(hx + s, hy + 6), (hx + s * 1.3, hy + 2), (hx + s * 0.7, hy + 10)], hc)
    else:   # short
        E(d, hx - 6, hy, hx + 6, hy + 14, hc)
        E(d, hx - 4, hy, hx + 2, hy + 4, mix(hc, (255, 255, 255), 0.15))
    hat_back(d, hx, hy, k)


def hat_back(d, hx, hy, k):
    h = k.hat
    if not h:
        return
    hc = k.hat_c
    if h == 'kasa':
        PG(d, [(hx - 15, hy + 7), (hx - 7, hy - 1), (hx, hy - 3), (hx + 7, hy - 1), (hx + 15, hy + 7), (hx, hy + 9)],
           C['straw'] if 'straw' in C else (212, 178, 108))
        for kk in (2, 5):
            LN(d, [(hx - 13 + kk, hy + 6 - kk // 2), (hx, hy + 7 - kk), (hx + 13 - kk, hy + 6 - kk // 2)], (166, 130, 74))
        R(d, hx - 14, hy + 8, hx + 14, hy + 8, (166, 130, 74))
    elif h == 'eboshi':
        PG(d, [(hx - 4, hy + 4), (hx + 4, hy + 4), (hx + 4, hy - 4), (hx + 1, hy - 11), (hx - 3, hy - 9), (hx - 4, hy - 3)],
           (30, 26, 30))
        PX(d, hx - 1, hy - 6, (70, 66, 72))
    elif h == 'kanmuri':
        R(d, hx - 5, hy - 2, hx + 5, hy + 4, (30, 26, 30))
        R(d, hx - 2, hy - 5, hx + 2, hy - 2, (30, 26, 30))
        R(d, hx - 1, hy + 4, hx + 1, hy + 24, (30, 26, 30))
    elif h == 'flatcap':
        E(d, hx - 7, hy - 1, hx + 7, hy + 7, hc)
        R(d, hx - 7, hy + 4, hx + 7, hy + 5, shade(hc, 0.8))
        for x in range(hx - 5, hx + 6, 3):
            PX(d, x, hy + 1, shade(hc, 1.2))
    elif h == 'zukin':
        E(d, hx - 7, hy - 3, hx + 7, hy + 7, hc)
        R(d, hx - 7, hy + 3, hx + 7, hy + 4, shade(hc, 0.75))
    elif h == 'headband':
        R(d, hx - 6, hy + 4, hx + 6, hy + 5, hc)


def head_profile(d, hx, hy, f, k, mouth=0, blink=False):
    """Profile head facing f (+1 right)."""
    p = Pen(d, hx, f)
    hs, hc = k.hair, k.hair_c
    sk = k.skin
    if k.kind == 'kappa':
        p.ell(-6, hy, 5, hy + 14, sk)
        p.poly([(4, hy + 8), (11, hy + 9), (10, hy + 12), (4, hy + 12)], (232, 196, 70))
        p.line([(5, hy + 10), (10, hy + 10)], (180, 140, 40))
        p.ell(-7, hy + 1, 5, hy + 7, (52, 92, 56))
        p.ell(-5, hy - 1, 4, hy + 3, (226, 222, 196))
        if not k.get('spilled'):
            p.ell(-3, hy, 2, hy + 2, (110, 170, 220))
        p.rect(2, hy + 6, 3, hy + 7, C['dark'] if not blink else sk)
        if blink:
            p.rect(1, hy + 7, 3, hy + 7, C['dark'])
        if mouth:
            p.rect(6, hy + 12, 9, hy + 13, (120, 50, 40))
        return
    # face
    p.ell(-4, hy + 1, 6, hy + 14, sk)
    p.px(7, hy + 8, sk)
    p.px(7, hy + 9, k.skin_dk)
    # ear
    p.rect(-2, hy + 7, -1, hy + 9, k.skin_dk)
    # eye
    if blink:
        p.rect(2, hy + 7, 4, hy + 7, C['dark'])
    else:
        p.rect(3, hy + 6, 4, hy + 7, C['dark'])
        p.px(3, hy + 6, (150, 140, 150))
    if k.glasses:
        gc = (60, 54, 52)
        p.rect(1, hy + 5, 5, hy + 5, gc)
        p.rect(1, hy + 8, 5, hy + 8, gc)
        p.rect(1, hy + 5, 1, hy + 8, gc)
        p.rect(5, hy + 5, 5, hy + 8, gc)
        p.line([(1, hy + 6), (-2, hy + 6)], gc)
    # mouth
    if mouth:
        p.rect(4, hy + 11, 5, hy + 12, (110, 40, 40))
    else:
        p.rect(4, hy + 11, 5, hy + 11, C['mouth'])
    if k.get('blush'):
        p.rect(2, hy + 9, 3, hy + 9, C['blush'])
    # beard
    b = k.beard
    if b == 'mustache':
        p.rect(3, hy + 10, 6, hy + 10, k.beard_c)
    elif b == 'goatee':
        p.rect(4, hy + 12, 5, hy + 14, k.beard_c)
    elif b == 'full':
        p.ell(-1, hy + 8, 6, hy + 15, k.beard_c)
        p.rect(4, hy + 11, 5, hy + 11, (110, 40, 40) if mouth else shade(k.beard_c, 0.7))
    elif b == 'long_white':
        p.poly([(0, hy + 9), (6, hy + 10), (5, hy + 22), (2, hy + 20)], k.beard_c)
        p.rect(3, hy + 10, 6, hy + 10, k.beard_c)
    # hair
    if hs == 'bald':
        p.ell(-4, hy + 6, 0, hy + 11, hc)
        p.px(2, hy + 2, mix(sk, (255, 255, 255), 0.4))
    elif hs in ('chonmage', 'topknot_band'):
        p.ell(-6, hy, 1, hy + 12, hc)
        p.ell(-3, hy, 4, hy + 4, SHAVED)
        p.rect(-2, hy - 2, 3, hy - 1, hc)
        p.rect(1, hy + 5, 1, hy + 8, hc)
        if hs == 'topknot_band':
            p.rect(-5, hy + 4, 5, hy + 5, (236, 232, 220))
    elif hs == 'wild':
        p.ell(-8, hy - 1, 3, hy + 12, hc)
        for sx_, sy_ in ((-9, 3), (-9, 9), (-6, -2), (0, -2)):
            p.poly([(sx_, hy + sy_), (sx_ + 3, hy + sy_ + 2), (sx_ + 3, hy + sy_ - 2)], hc)
        p.poly([(-7, hy + 3), (-13, hy + 1), (-12, hy + 4), (-7, hy + 6)], hc)
        p.rect(1, hy + 2, 5, hy + 4, hc)
    elif hs in ('long', 'heian'):
        p.ell(-7, hy, 3, hy + 13, hc)
        p.rect(0, hy + 1, 5, hy + 3, hc)
        p.rect(4, hy + 3, 5, hy + 4, hc)
        p.rect(-7, hy + 7, -2, 136 if hs == 'heian' and hy > 90 else hy + 26, hc)
    elif hs == 'bun':
        p.ell(-6, hy, 3, hy + 12, hc)
        p.ell(-10, hy + 3, -4, hy + 9, shade(hc, 0.85))
        p.rect(0, hy + 1, 5, hy + 3, hc)
    elif hs == 'ponytail':
        p.ell(-6, hy, 3, hy + 12, hc)
        p.rect(0, hy + 1, 5, hy + 4, hc)
        p.px(5, hy + 5, hc)
        p.poly([(-6, hy + 3), (-12, hy + 6), (-11, hy + 16), (-8, hy + 13), (-6, hy + 7)], hc)
        p.rect(-7, hy + 3, -6, hy + 5, k.get('tie_c', (200, 60, 60)))
    elif hs == 'bob':
        p.ell(-7, hy - 1, 5, hy + 12, hc)
        p.rect(-7, hy + 5, -1, hy + 13, hc)
        p.rect(1, hy + 2, 6, hy + 5, hc)
    elif hs == 'okuni':
        p.ell(-6, hy, 3, hy + 12, hc)
        p.rect(0, hy + 1, 5, hy + 3, hc)
        p.poly([(-6, hy + 2), (-12, hy + 4), (-11, hy + 20), (-7, hy + 10)], hc)
        p.rect(-7, hy + 2, -6, hy + 4, (230, 200, 60))
    elif hs == 'hood':
        p.ell(-7, hy, 3, hy + 13, k.hat_c)
        p.rect(-1, hy, 4, hy + 3, k.hat_c)
        p.rect(-6, hy + 7, 0, hy + 7, shade(k.hat_c, 0.75))
    elif hs == 'horns':
        p.ell(-8, hy - 1, 3, hy + 12, hc)
        p.poly([(0, hy + 1), (4, hy - 7), (3, hy + 1)], (236, 220, 180))
        for sy_ in (2, 7, 12):
            p.poly([(-8, hy + sy_), (-13, hy + sy_ - 2), (-12, hy + sy_ + 3)], hc)
        p.rect(2, hy + 5, 5, hy + 5, hc)
    else:   # short
        p.ell(-6, hy, 3, hy + 11, hc)
        p.rect(0, hy + 1, 5, hy + 3, hc)
    hat_profile(d, hx, hy, f, k)


def hat_profile(d, hx, hy, f, k):
    h = k.hat
    if not h:
        return
    p = Pen(d, hx, f)
    hc = k.hat_c
    if h == 'kasa':
        p.poly([(-15, hy + 4), (0, hy - 5), (15, hy + 4), (0, hy + 5)], (212, 178, 108))
        p.line([(-12, hy + 3), (0, hy - 2), (12, hy + 3)], (166, 130, 74))
        p.line([(-15, hy + 4), (15, hy + 4)], (166, 130, 74))
    elif h == 'eboshi':
        p.poly([(-5, hy + 4), (3, hy + 4), (2, hy - 3), (-3, hy - 11), (-6, hy - 8), (-6, hy - 2)], (30, 26, 30))
        p.px(-3, hy - 6, (70, 66, 72))
    elif h == 'kanmuri':
        p.rect(-5, hy - 2, 4, hy + 4, (30, 26, 30))
        p.rect(-3, hy - 5, 0, hy - 2, (30, 26, 30))
        p.line([(-5, hy - 1), (-12, hy + 10), (-12, hy + 22)], (30, 26, 30), 2)
    elif h == 'flatcap':
        p.ell(-7, hy - 1, 6, hy + 6, hc)
        p.rect(3, hy + 3, 9, hy + 4, shade(hc, 0.8))
        p.rect(-6, hy + 5, -3, hy + 9, k.hair_c)
    elif h == 'zukin':
        p.ell(-7, hy - 3, 6, hy + 6, hc)
        p.rect(-7, hy + 3, 5, hy + 4, shade(hc, 0.75))
    elif h == 'headband':
        p.rect(-6, hy + 4, 5, hy + 5, hc)
        p.rect(-8, hy + 5, -6, hy + 9, hc)


# ============================================================================ seated bodies (from behind)
def body_back(d, sx, k, dy=0, t=0.0):
    top = 113 + dy
    c1, c2 = k.c1, k.c2
    b = k.body
    wide = b in ('kariginu', 'junihitoe', 'robe_wide')
    sh, hip = (11, 15) if wide else (9, 12)
    if k.kind == 'raijin':
        sh, hip = 11, 13
    # torso
    if b == 'loincloth':
        PG(d, [(sx - sh, top), (sx + sh, top), (sx + hip, 124), (sx + hip, 138), (sx - hip, 138), (sx - hip, 124)], k.skin)
        PG(d, [(sx + sh - 3, top), (sx + sh, top), (sx + hip, 124), (sx + hip, 138), (sx + hip - 4, 138)], k.skin_dk)
        R(d, sx - hip, 128, sx + hip, 138, (232, 184, 60))
        for x in range(sx - hip + 2, sx + hip, 4):
            R(d, x, 129, x + 1, 137, (60, 40, 30))
        R(d, sx - hip, 127, sx + hip, 128, (200, 60, 50))
        for s in (-1, 1):
            R(d, sx + s * (sh + 1) - (2 if s > 0 else 2), top + 3, sx + s * (sh + 4), 132, k.skin_dk if s > 0 else k.skin)
        return
    PG(d, [(sx - sh, top), (sx + sh, top), (sx + hip, 122), (sx + hip, 138), (sx - hip, 138), (sx - hip, 122)], c1)
    PG(d, [(sx + sh - 2, top), (sx + sh, top), (sx + hip, 122), (sx + hip, 138), (sx + hip - 3, 138)], c2)
    # arms / sleeves
    if wide:
        for s in (-1, 1):
            PG(d, [(sx + s * sh, top + 2), (sx + s * (sh + 6), top + 8), (sx + s * (sh + 6), 134), (sx + s * sh, 134)],
               c2 if s > 0 else shade(c1, 0.9))
    else:
        R(d, sx - 14, top + 3, sx - 11, 132, shade(c1, 0.88))
        R(d, sx + 11, top + 3, sx + 14, 132, c2)
    # details by style
    if b == 'kimono':
        R(d, sx - hip + 1, 126, sx + hip - 1, 129, k.sash)
        if k.bow_obi:
            R(d, sx - 5, 123, sx + 5, 132, shade(k.sash, 0.85))
            R(d, sx - 4, 124, sx + 4, 125, mix(k.sash, (255, 255, 255), 0.25))
    elif b in ('haori', 'samue'):
        if k.crest:
            E(d, sx - 3, top + 5, sx + 2, top + 10, k.crest)
            E(d, sx - 2, top + 6, sx + 1, top + 9, c1)
    elif b == 'kamishimo':
        for s in (-1, 1):
            PG(d, [(sx + s * 4, top), (sx + s * 16, top - 1), (sx + s * 15, top + 4), (sx + s * 9, top + 6)], k.c2)
        LN(d, [(sx, top + 1), (sx, 125)], shade(c1, 0.7))
        R(d, sx - hip + 1, 126, sx + hip - 1, 128, k.sash)
        if k.get('dandara'):
            for i, x in enumerate(range(sx - hip, sx + hip, 4)):
                PG(d, [(x, 138), (x + 2, 133), (x + 4, 138)], (236, 232, 222))
    elif b == 'uniform':
        PG(d, [(sx - 8, top), (sx + 8, top), (sx + 8, top + 10), (sx - 8, top + 10)], k.c1)
        R(d, sx - 8, top + 8, sx + 8, top + 8, (236, 236, 240))
        R(d, sx - 8, top, sx - 8, top + 8, (236, 236, 240))
        R(d, sx + 8, top, sx + 8, top + 8, (236, 236, 240))
        R(d, sx - 9, 126, sx + 9, 138, k.get('skirt', (52, 56, 84)))
        for x in range(sx - 9, sx + 10, 3):
            R(d, x, 128, x, 138, shade(k.get('skirt', (52, 56, 84)), 0.8))
    elif b == 'jumper':
        R(d, sx - hip, 134, sx + hip, 138, shade(c1, 1.12))
        for x in range(sx - hip, sx + hip + 1, 2):
            PX(d, x, 135, shade(c1, 0.85))
        R(d, sx - 3, top, sx + 2, top + 1, shade(c1, 1.15))
    elif b == 'suit':
        LN(d, [(sx, top + 2), (sx, 138)], shade(c1, 0.7))
        R(d, sx - 3, top - 1, sx + 2, top, (238, 236, 230))
    elif b == 'dress':
        for s in (-1, 1):
            E(d, sx + s * 9 - 4, top - 1, sx + s * 9 + 4, top + 6, shade(c1, 1.1))
        R(d, sx - 3, top - 3, sx + 2, top, c1)
        R(d, sx - hip - 1, 130, sx + hip + 1, 138, c2)
    elif b == 'fisher':
        R(d, sx - 14, 124, sx - 11, 132, k.skin)
        R(d, sx + 11, 124, sx + 14, 132, k.skin_dk)
        LN(d, [(sx - hip, 127), (sx + hip, 126)], (200, 180, 130), 2)
    elif b == 'armor':
        for y in range(top + 4, 136, 4):
            R(d, sx - hip + 1, y, sx + hip - 1, y, shade(c1, 0.65))
            for x in range(sx - hip + 3, sx + hip - 1, 4):
                PX(d, x, y + 2, k.get('lace', (180, 60, 50)))
    elif b == 'kariginu':
        E(d, sx - 4, top - 2, sx + 3, top + 2, shade(c1, 0.8))
        R(d, sx - hip, 128, sx + hip, 129, k.sash)
    elif b == 'junihitoe':
        lay = k.layers or [(220, 120, 140), (240, 200, 120), (120, 160, 110)]
        for i, lc in enumerate(lay):
            R(d, sx - hip - 1 + i, 136 - i * 2, sx + hip + 1 - i, 138 - i * 2, lc)
    elif b == 'robe':
        pass


def draw_seated(d, sx, k, st, t):
    """A person (or human-shaped folk) on a stool, seen from behind."""
    dy = st.get('dy', 0)
    hdy = st.get('hdy', 0)
    head = st.get('head', 'back')
    hy = 97 + dy + hdy
    if k.kind == 'kappa':
        E(d, sx - 12, 112 + dy, sx + 12, 139, (110, 120, 70))
        for (a, b) in ((-6, 118), (2, 118), (-2, 126), (6, 126), (-8, 130), (0, 132)):
            E(d, sx + a - 3, b + dy, sx + a + 3, b + 5 + dy, (140, 150, 90))
        R(d, sx - 14, 116 + dy, sx - 11, 132, k.skin)
        R(d, sx + 11, 116 + dy, sx + 14, 132, shade(k.skin, 0.8))
    elif k.kind == 'tanuki':
        draw_tanuki_seated(d, sx, k, st, t)
        return
    elif k.kind == 'gfox':
        draw_gfox_seated(d, sx, k, st, t)
        return
    else:
        if k.kind == 'raijin':
            draw_drum_ring(d, sx, hy + 6, t)
        body_back(d, sx, k, dy, t)
        if k.size < 1.0:
            pass
    if k.prop == 'staff_lean':
        pass
    if head == 'back':
        head_back(d, sx, hy, k)
    else:
        head_profile(d, sx, hy, 1 if head == 'right' else -1, k, st.get('mouth', 0), st.get('blink', False))
    if k.get('paper'):
        # reading a newspaper: its edges show either side of the head
        for s in (-1, 1):
            x0 = sx + s * 9
            R(d, x0, 96 + dy, x0 + s * 6, 118 + dy, (236, 232, 220))
            for y in range(99 + dy, 116 + dy, 3):
                R(d, x0 + s * 1, y, x0 + s * 5, y, (150, 146, 140))
        R(d, sx - 15, 112 + dy, sx - 12, 118 + dy, k.skin)
        R(d, sx + 12, 112 + dy, sx + 15, 118 + dy, k.skin)


def draw_drum_ring(d, cx, cy, t):
    r = 22
    for i in range(9):
        a = math.pi * (1.05 + 0.9 * i / 8)
        x = cx + r * math.cos(a)
        y = cy + r * 0.85 * math.sin(a)
        E(d, x - 4, y - 4, x + 4, y + 4, (176, 60, 44))
        E(d, x - 2, y - 2, x + 2, y + 2, (232, 196, 90))
        PX(d, x, y, (176, 60, 44))
    LN(d, [(cx + r * math.cos(math.pi * (1.05 + 0.9 * i / 16)), cy + r * 0.85 * math.sin(math.pi * (1.05 + 0.9 * i / 16)))
           for i in range(17)], (120, 80, 40))


# ============================================================================ walking (side view)
def draw_walker(d, x, fy, f, k, st, t):
    """Full body from the side, feet on y = fy, facing f."""
    cx, fy = int(round(x)), int(round(fy))
    ph = st.get('phase', 0.0)
    s_ = math.sin(ph * math.pi)
    bob = 1 if abs(s_) > 0.7 else 0
    p = Pen(d, cx, f)
    kind = k.kind
    if kind == 'tanuki':
        draw_tanuki_walk(d, cx, fy, f, k, st, t)
        return
    if kind == 'gfox':
        draw_gfox_walk(d, cx, fy, f, k, st, t)
        return
    small = k.size < 1.0
    top = fy - (34 if small else 48) - bob
    hy = top - (13 if small else 14)
    if kind == 'raijin':
        draw_drum_ring(d, cx - f * 2, hy + 10, t)
    # back props
    if k.prop == 'box':
        pass
    if kind == 'kappa':
        p.ell(-10, top + 1, -2, top + 22, (110, 120, 70))
    b = k.body
    c1, c2 = k.c1, k.c2
    legs_bare = b in ('fisher', 'loincloth') or kind == 'kappa'
    # legs / feet
    foot = (230, 226, 216) if kind == 'human' else shade(k.skin, 0.9)
    if b in ('suit',):
        foot = (40, 34, 36)
    for sgn in (1, -1):
        off = 3 * s_ * sgn
        if legs_bare:
            p.rect(-4 + off, fy - 12, -1 + off, fy - 1, k.skin if sgn > 0 else k.skin_dk)
            p.rect(-5 + off, fy, 0 + off, fy, foot if kind != 'kappa' else (80, 130, 76))
        elif b in ('suit',):
            p.rect(-4 + off, fy - 16, -1 + off, fy - 1, shade(c1, 0.8 if sgn > 0 else 0.65))
            p.rect(-5 + off, fy, 1 + off, fy, foot)
        elif b == 'uniform':
            p.rect(-4 + off, fy - 10, -2 + off, fy - 2, k.skin)
            p.rect(-4 + off, fy - 4, -2 + off, fy - 1, (236, 236, 240))
            p.rect(-5 + off, fy, 0 + off, fy, (60, 40, 36))
        else:
            p.rect(-6 + off * 0.7, fy - 3, -2 + off * 0.7, fy - 1, (236, 232, 222) if kind == 'human' else foot)
            p.rect(-7 + off * 0.7, fy, -1 + off * 0.7, fy, (110, 74, 46))
    # body
    if b == 'loincloth':
        p.poly([(-7, top), (7, top), (8, fy - 14), (-8, fy - 14)], k.skin)
        p.rect(-8, fy - 18, 8, fy - 10, (232, 184, 60))
        for xx in (-6, -2, 2, 6):
            p.rect(xx, fy - 17, xx, fy - 11, (60, 40, 30))
    elif b in ('suit',):
        p.poly([(-6, top), (6, top), (7, fy - 14), (-7, fy - 14)], c1)
        p.rect(1, top, 3, top + 6, (238, 236, 230))
    elif b == 'dress':
        p.poly([(-6, top), (6, top), (7, fy - 22), (10, fy - 1), (-10, fy - 1), (-7, fy - 22)], c1)
        p.ell(-3, top - 1, 5, top + 6, shade(c1, 1.1))
    elif b == 'uniform':
        p.poly([(-6, top), (6, top), (7, fy - 20), (-7, fy - 20)], c1)
        p.poly([(-7, fy - 20), (7, fy - 20), (9, fy - 10), (-9, fy - 10)], k.get('skirt', (52, 56, 84)))
        p.rect(3, top + 1, 6, top + 6, (200, 50, 50))
        p.rect(-7, top, -2, top + 8, k.c1)
        p.rect(-7, top + 7, -2, top + 7, (236, 236, 240))
    elif b == 'fisher':
        p.poly([(-7, top), (7, top), (8, fy - 12), (-8, fy - 12)], c1)
        p.line([(-8, top + 14), (8, top + 13)], (200, 180, 130), 2)
    elif b == 'junihitoe':
        lay = k.layers or [(220, 120, 140), (240, 200, 120), (120, 160, 110)]
        p.poly([(-7, top), (7, top), (11, fy), (-13, fy)], c1)
        for i, lc in enumerate(lay):
            p.rect(-13 + i, fy - 2 - i * 2, 11 - i, fy - i * 2, lc)
    else:
        wide = b in ('kariginu', 'robe_wide')
        p.poly([(-7, top), (7, top), (9 if not wide else 11, fy - 4), (-9 if not wide else -11, fy - 4)], c1)
        p.poly([(-7, top), (-4, top), (-6, fy - 4), (-9, fy - 4)], c2)
        if b == 'kimono':
            p.rect(-7, top + 15, 7, top + 18, k.sash)
            if k.bow_obi:
                p.rect(-10, top + 13, -6, top + 21, shade(k.sash, 0.85))
        elif b == 'kamishimo':
            p.poly([(-2, top), (12, top - 2), (11, top + 3), (2, top + 5)], c2)
            p.poly([(2, top), (-12, top - 2), (-11, top + 3), (-2, top + 5)], c2)
            if k.get('dandara'):
                for xx in range(-9, 9, 4):
                    p.poly([(xx, fy - 4), (xx + 2, fy - 9), (xx + 4, fy - 4)], (236, 232, 222))
        elif b == 'jumper':
            p.rect(-8, fy - 22, 8, fy - 19, shade(c1, 1.12))
        elif b == 'armor':
            for yy in range(top + 4, fy - 6, 4):
                p.rect(-7, yy, 8, yy, shade(c1, 0.65))
    if kind == 'kappa':
        p.ell(-11, top + 1, -3, top + 22, (110, 120, 70))
        for (a, bb) in ((-8, 4), (-6, 12)):
            p.ell(a - 2, top + bb, a + 2, top + bb + 4, (140, 150, 90))
    # arm
    arm_c = c2 if b not in ('loincloth', 'fisher') else k.skin_dk
    if kind == 'kappa':
        arm_c = shade(k.skin, 0.85)
    p.poly([(0 - s_, top + 2), (6 - s_, top + 4), (7 - 2 * s_, top + 15), (1 - 2 * s_, top + 15)], arm_c)
    p.ell(5 - 2 * s_, top + 13, 9 - 2 * s_, top + 17, k.skin)
    # front props
    pr = k.prop
    if pr == 'staff':
        p.line([(9, fy - 76 + (14 if small else 0)), (9, fy)], (126, 92, 60), 2)
    elif pr == 'cane':
        p.line([(9, top + 12), (12, fy)], (110, 80, 50), 2)
    elif pr == 'spear':
        p.line([(10, fy - 80), (8, fy)], (110, 80, 50), 1)
        p.poly([(10, fy - 88), (12, fy - 80), (8, fy - 80)], (200, 200, 210))
    elif pr == 'oar':
        p.line([(-6, top + 2), (10, top - 26)], (170, 130, 80), 2)
    elif pr == 'box':
        p.rect(5, top + 10, 13, top + 18, (40, 30, 34))
        p.rect(5, top + 13, 13, top + 13, (200, 60, 50))
        p.rect(8, top + 10, 9, top + 18, (200, 60, 50))
    elif pr == 'fan':
        p.poly([(8, top + 12), (16, top + 4), (17, top + 12)], (230, 80, 70))
    elif pr == 'plum':
        p.line([(8, top + 14), (14, top - 2), (18, top - 6)], (90, 60, 40))
        for (a, bb) in ((14, -2), (17, -6), (12, 3)):
            p.rect(a, top + bb, a + 1, top + bb + 1, (250, 170, 190))
    elif pr == 'brush':
        p.line([(8, top + 15), (11, top + 8)], (110, 80, 50))
        p.px(11, top + 7, C['dark'])
    elif pr == 'swords':
        p.line([(-4, top + 15), (-13, top + 11)], (40, 30, 34), 2)
        p.line([(-4, top + 17), (-10, top + 15)], (40, 30, 34), 2)
    # head
    head_profile(d, cx, hy, f, k, st.get('mouth', 0), st.get('blink', False))


# ============================================================================ fox folk (Kon, Grandmother)
def fox_tail(d, pts, c=C['fur'], tipc=C['fur_lt'], w=1.0):
    path = bez(*pts, 14)
    for i, (x, y) in enumerate(path):
        u = i / 13
        r = (3.5 + 2.0 * math.sin(u * math.pi) - 1.0 * u) * w
        E(d, x - r, y - r, x + r, y + r, c if u < 0.68 else tipc)


def fox_head_back(d, hx, hy, t, perk=False, fur=C['fur'], fur_dk=C['fur_dk'], tip=C['tip']):
    tw = 1 if (math.sin(t * 0.9 + 1.3) > 0.97) else 0
    up = 2 if perk else 0
    PG(d, [(hx - 7, hy + 4), (hx - 5 - tw, hy - 8 - up), (hx - 1, hy + 2)], fur)
    PG(d, [(hx - 6, hy - 3 - up), (hx - 5 - tw, hy - 8 - up), (hx - 4, hy - 3 - up)], tip)
    PG(d, [(hx + 6, hy + 4), (hx + 4, hy - 8 - up), (hx, hy + 2)], fur)
    PG(d, [(hx + 5, hy - 3 - up), (hx + 4, hy - 8 - up), (hx + 3, hy - 3 - up)], tip)
    E(d, hx - 7, hy, hx + 6, hy + 15, fur)
    R(d, hx - 5, hy + 13, hx + 4, hy + 14, fur_dk)


def fox_head_profile(d, hx, hy, f, t, mouth=0, fur=C['fur'], fur_dk=C['fur_dk'], lt=C['fur_lt'], tip=C['tip'],
                     marks=None, blink=False):
    tw = 1 if (math.sin(t * 0.9 + 1.3) > 0.97) else 0
    p = Pen(d, hx, f)
    p.poly([(-5, hy + 4), (-3, hy - 9), (1, hy + 2)], fur_dk)
    p.ell(-6, hy, 6, hy + 14, fur)
    p.poly([(-4, hy + 3), (-2 + tw, hy - 9), (2, hy + 2)], fur)
    p.poly([(-3, hy - 4), (-2 + tw, hy - 9), (-1, hy - 4)], tip)
    p.poly([(3, hy + 6), (11, hy + 9), (11, hy + 11), (4, hy + 13)], fur)
    p.poly([(2, hy + 10), (10, hy + 11), (4, hy + 14)], lt)
    p.ell(-2, hy + 8, 3, hy + 13, lt)
    p.rect(11, hy + 8, 12, hy + 9, C['dark'])
    if blink:
        p.rect(1, hy + 6, 3, hy + 6, C['dark'])
    else:
        p.rect(2, hy + 5, 3, hy + 5, C['dark'])
        p.px(4, hy + 6, C['dark'])
    if marks:
        p.line([(1, hy + 3), (4, hy + 4)], marks)
    if mouth:
        p.rect(7, hy + 12, 9, hy + 12, (110, 40, 40))


def draw_kon(d, s, t):
    """Kon the fox: seated (s['mode'] == 'sit') or walking; s['variant'] for disguises."""
    var = s.get('variant')
    tails = int(s.get('tails', 1))
    if s['mode'] == 'sit':
        sx = int(s['x'])
        dy = s.get('dy', 0)
        sw = math.sin(t * 1.7)
        if var in ('human_fail', 'heian_fail', 'gen_fail', 'human'):
            k = KON_DISGUISE[var]
            body_back(d, sx, k, dy, t)
            if var != 'human' or tails:
                for i in range(tails if var != 'human' else 0):
                    fox_tail(d, [(sx + 6, 133), (sx + 17 + 2 * sw + i * 4, 136 - i * 6), (sx + 20 + 3 * sw + i * 6, 150 - i * 8),
                                 (sx + 13 + 4 * sw + i * 7, 160 - i * 8)])
            hy = 97 + s.get('hdy', 0) + dy
            head = s.get('head', 'back')
            if head == 'back':
                head_back(d, sx, hy, k)
            else:
                head_profile(d, sx, hy, 1 if head == 'right' else -1, k, s.get('mouth', 0), s.get('blink', False))
            if var != 'human':
                for sgn in (-1, 1):
                    PG(d, [(sx + sgn * 6, hy + 3), (sx + sgn * 5, hy - 7), (sx + sgn * 1, hy + 1)], C['fur'])
                    PG(d, [(sx + sgn * 5, hy - 3), (sx + sgn * 5, hy - 7), (sx + sgn * 3, hy - 3)], C['tip'])
            return
        PG(d, [(sx - 9, 113 + dy), (sx + 9, 113 + dy), (sx + 12, 122), (sx + 12, 138), (sx - 12, 138), (sx - 12, 122)], C['haori'])
        PG(d, [(sx + 7, 113 + dy), (sx + 9, 113 + dy), (sx + 12, 122), (sx + 12, 138), (sx + 8, 138)], C['haori_dk'])
        R(d, sx - 14, 116 + dy, sx - 11, 132, C['haori_dk'])
        R(d, sx + 11, 116 + dy, sx + 14, 132, C['haori_dk'])
        E(d, sx - 3, 118 + dy, sx + 2, 123 + dy, C['white'])
        E(d, sx - 2, 119 + dy, sx + 1, 122 + dy, C['haori'])
        for i in range(tails):
            fox_tail(d, [(sx + 6 - i * 12, 133), (sx + 17 + 2 * sw - i * 30, 136 - i * 2),
                         (sx + 20 + 3 * sw - i * 34, 150), (sx + 13 + 4 * sw - i * 28, 160)])
        E(d, sx - 6, 109 + dy, sx + 5, 115 + dy, C['fur_lt'])
        hy = 97 + s.get('hdy', 0) + dy
        head = s.get('head', 'back')
        if head == 'back':
            fox_head_back(d, sx, hy, t, s.get('perk', False))
        else:
            fox_head_profile(d, sx, hy, 1 if head == 'right' else -1, t, s.get('mouth', 0), blink=s.get('blink', False))
    else:
        cx, fy, f = int(s['x']), int(s['y']), s['f']
        ph = s.get('phase', 0.0)
        st_ = math.sin(ph * math.pi)
        bob = 1 if abs(st_) > 0.7 else 0
        p = Pen(d, cx, f)
        sw = math.sin(t * 3)
        for i in range(tails):
            fox_tail(d, [(cx - f * 5, fy - 30), (cx - f * (15 + 2 * i), fy - 30 + sw - 4 * i),
                         (cx - f * (22 + 3 * i), fy - 38 + sw - 4 * i), (cx - f * (22 + 2 * i), fy - 48 + 2 * sw - 3 * i)])
        p.poly([(-7, fy - 47 - bob), (7, fy - 47 - bob), (8, fy - 22), (-8, fy - 22)], C['haori'])
        p.poly([(-6, fy - 22), (6, fy - 22), (7, fy - 3), (-7, fy - 3)], C['cream'])
        p.rect(-6, fy - 24, 6, fy - 21, C['haori_dk'])
        p.rect(-7 + 3 * st_, fy - 3, -3 + 3 * st_, fy - 1, (230, 226, 216))
        p.rect(-7 + 3 * st_, fy, -2 + 3 * st_, fy, (100, 64, 40))
        p.rect(2 - 3 * st_, fy - 3, 6 - 3 * st_, fy - 1, (230, 226, 216))
        p.rect(2 - 3 * st_, fy, 7 - 3 * st_, fy, (100, 64, 40))
        p.poly([(0 - st_, fy - 45 - bob), (6 - st_, fy - 43 - bob), (7 - 2 * st_, fy - 31), (0 - 2 * st_, fy - 31)], C['haori_dk'])
        p.ell(-5, fy - 50 - bob, 5, fy - 44 - bob, C['fur_lt'])
        fox_head_profile(d, cx, fy - 62 - bob, f, t, s.get('mouth', 0))


KON_DISGUISE = {
    'human_fail': L(hair='short', hair_c=(214, 120, 52), body='haori', c1=C['haori'], c2=C['haori_dk'], crest=C['white']),
    'heian_fail': L(hair='heian', hair_c=(214, 120, 52), body='junihitoe', c1=(200, 90, 110),
                    layers=[(240, 200, 120), (120, 160, 110), (230, 140, 160)]),
    'gen_fail': L(hair='short', hair_c=GREY, hat='flatcap', hat_c=(120, 100, 80), body='jumper', c1=(130, 90, 60), glasses=True),
    'human': L(hair='short', hair_c=(196, 104, 50), body='haori', c1=C['haori'], c2=C['haori_dk'], crest=C['white']),
}


def draw_gfox_seated(d, sx, k, st, t):
    dy = st.get('dy', 0)
    hy = 97 + dy + st.get('hdy', 0)
    sw = math.sin(t * 1.3)
    for i in range(9):
        a = math.pi * (0.12 + 0.76 * i / 8)
        r = 24 + 2 * math.sin(t * 1.1 + i)
        ex, ey = sx + r * math.cos(a) * 1.05, 126 - r * 0.9 * math.sin(a)
        fox_tail(d, [(sx, 132), (sx + (ex - sx) * 0.3, 130), (sx + (ex - sx) * 0.8, ey + 8 + sw), (ex, ey)],
                 c=(244, 240, 236), tipc=(250, 250, 250), w=0.55)
    body_back(d, sx, k, dy, t)
    head = st.get('head', 'back')
    if head == 'back':
        fox_head_back(d, sx, hy, t, fur=(244, 240, 236), fur_dk=(214, 210, 206), tip=(200, 70, 70))
    else:
        fox_head_profile(d, sx, hy, 1 if head == 'right' else -1, t, st.get('mouth', 0), fur=(244, 240, 236),
                         fur_dk=(214, 210, 206), lt=(255, 255, 255), tip=(200, 70, 70), marks=(210, 60, 60),
                         blink=st.get('blink', False))


def draw_gfox_walk(d, cx, fy, f, k, st, t):
    ph = st.get('phase', 0.0)
    s_ = math.sin(ph * math.pi)
    p = Pen(d, cx, f)
    for i in range(9):
        a = math.pi * (0.55 + 0.5 * i / 8)
        fox_tail(d, [(cx - f * 4, fy - 26), (cx - f * (10 + i), fy - 30 - i), (cx - f * (16 + 2 * i), fy - 40 - i * 2),
                     (cx - f * (12 + 2 * i), fy - 50 - i * 2)], c=(244, 240, 236), tipc=(255, 255, 255), w=0.7)
    p.poly([(-7, fy - 47), (7, fy - 47), (9, fy - 1), (-10, fy - 1)], k.c1)
    p.poly([(-7, fy - 47), (-4, fy - 47), (-6, fy - 1), (-10, fy - 1)], k.c2)
    p.rect(-7, fy - 32, 7, fy - 29, k.sash)
    p.poly([(0, fy - 45), (6, fy - 43), (7, fy - 31), (1, fy - 31)], k.c2)
    p.ell(-5, fy - 50, 5, fy - 44, (255, 255, 255))
    fox_head_profile(d, cx, fy - 62, f, t, st.get('mouth', 0), fur=(244, 240, 236), fur_dk=(214, 210, 206),
                     lt=(255, 255, 255), tip=(200, 70, 70), marks=(210, 60, 60))


# ============================================================================ tanuki
TAN = (130, 96, 66)
TAN_DK = (92, 66, 46)
TAN_LT = (214, 190, 150)


def tanuki_head_profile(d, hx, hy, f, mouth=0, blink=False, hat=True):
    p = Pen(d, hx, f)
    p.ell(-7, hy - 1, -2, hy + 4, TAN_DK)
    p.ell(-7, hy, 6, hy + 14, TAN)
    p.poly([(2, hy + 7), (10, hy + 9), (9, hy + 12), (2, hy + 13)], TAN_LT)
    p.rect(9, hy + 8, 10, hy + 9, C['dark'])
    p.poly([(-1, hy + 4), (6, hy + 5), (6, hy + 9), (-1, hy + 8)], (54, 40, 32))
    p.rect(3, hy + 6, 3, hy + 6 if blink else hy + 7, (240, 230, 210))
    if mouth:
        p.rect(6, hy + 12, 8, hy + 12, (110, 40, 40))
    if hat:
        p.poly([(-15, hy + 3), (0, hy - 6), (15, hy + 3), (0, hy + 4)], (212, 178, 108))
        p.line([(-15, hy + 3), (15, hy + 3)], (166, 130, 74))


def draw_tanuki_seated(d, sx, k, st, t):
    dy = st.get('dy', 0)
    hy = 97 + dy + st.get('hdy', 0)
    sw = math.sin(t * 1.5)
    # tail
    for i in range(6):
        y = 132 + i * 4
        x = sx + 12 + i * 1.5 + sw * (i / 5)
        E(d, x - 4, y - 3, x + 4, y + 3, TAN_DK if i % 2 else TAN)
    E(d, sx - 13, 110 + dy, sx + 13, 140, TAN)
    E(d, sx + 3, 112 + dy, sx + 13, 138, TAN_DK)
    R(d, sx - 15, 118 + dy, sx - 12, 130, TAN_DK)
    head = st.get('head', 'back')
    if head == 'back':
        E(d, sx - 7, hy - 1, sx - 2, hy + 4, TAN_DK)
        E(d, sx + 2, hy - 1, sx + 7, hy + 4, TAN_DK)
        E(d, sx - 7, hy, sx + 7, hy + 15, TAN)
        if k.hat:
            PG(d, [(sx - 15, hy + 6), (sx, hy - 4), (sx + 15, hy + 6), (sx, hy + 8)], (212, 178, 108))
            R(d, sx - 14, hy + 7, sx + 14, hy + 7, (166, 130, 74))
    else:
        tanuki_head_profile(d, sx, hy, 1 if head == 'right' else -1, st.get('mouth', 0), st.get('blink', False), k.hat)


def draw_tanuki_walk(d, cx, fy, f, k, st, t):
    ph = st.get('phase', 0.0)
    s_ = math.sin(ph * math.pi)
    p = Pen(d, cx, f)
    for i in range(6):
        p.ell(-14 - i * 2, fy - 22 + i * 3, -6 - i * 2, fy - 16 + i * 3, TAN_DK if i % 2 else TAN)
    for sgn in (1, -1):
        off = 2.5 * s_ * sgn
        p.rect(-5 + off, fy - 6, -1 + off, fy, TAN_DK)
    p.ell(-11, fy - 40, 11, fy - 4, TAN)
    p.ell(-2, fy - 32, 11, fy - 8, TAN_LT)
    p.rect(8, fy - 22, 13, fy - 15, (230, 220, 200))     # sake flask
    p.rect(9, fy - 24, 12, fy - 22, (230, 220, 200))
    p.rect(8, fy - 19, 13, fy - 19, (60, 60, 120))
    p.ell(4, fy - 28, 9, fy - 23, TAN_DK)
    tanuki_head_profile(d, cx, fy - 50, f, st.get('mouth', 0), st.get('blink', False), k.hat)


def draw_kettle(d, sx, t, wobble=0.0):
    """The tanuki as a tea kettle (Bunbuku chagama), sitting on a stool."""
    w = math.sin(t * 9) * wobble
    cy = 124
    for i in range(4):
        E(d, sx + 12 + i * 2 - 3, cy + 4 + i * 3 - 3, sx + 12 + i * 2 + 3, cy + 4 + i * 3 + 3, TAN_DK if i % 2 else TAN)
    E(d, sx - 12 + w, cy - 9, sx + 12 + w, cy + 10, (70, 66, 70))
    E(d, sx - 10 + w, cy - 7, sx + 4 + w, cy + 2, (96, 92, 98))
    R(d, sx - 6 + w, cy - 12, sx + 6 + w, cy - 9, (60, 56, 60))
    R(d, sx - 1 + w, cy - 15, sx + 1 + w, cy - 12, (60, 56, 60))
    PG(d, [(sx - 11 + w, cy - 1), (sx - 19 + w, cy - 8), (sx - 18 + w, cy - 5), (sx - 11 + w, cy + 3)], (70, 66, 70))
    LN(d, [(sx - 10 + w, cy - 9), (sx, cy - 20), (sx + 10 + w, cy - 9)], (50, 46, 50))
    E(d, sx + 6 + w, cy - 6, sx + 14 + w, cy + 2, TAN)
    PX(d, sx + 11 + w, cy - 3, C['dark'])
    for s in (-1, 1):
        R(d, sx + s * 6 - 1 + w, cy + 9, sx + s * 6 + 1 + w, cy + 12, TAN_DK)


# ============================================================================ one-off creatures
def draw_dog(d, x, y, f, st, t):
    """Hachikō: a cream Akita.  st['pose']: 'sit' (on the floor) or 'walk'."""
    p = Pen(d, int(round(x)), f)
    fur, fur_dk, lt = (236, 222, 196), (204, 184, 150), (250, 244, 232)
    y = int(round(y))
    if st.get('pose', 'sit') == 'sit':
        p.ell(-10, y - 22, 4, y - 2, fur)               # haunch
        p.ell(-2, y - 26, 8, y - 6, fur)                # chest
        p.ell(0, y - 20, 7, y - 8, lt)
        p.rect(3, y - 8, 5, y - 1, fur_dk)              # front leg
        p.rect(6, y - 8, 8, y - 1, fur)
        p.ell(-14, y - 26, -6, y - 16, fur_dk)          # curled tail
        p.ell(-12, y - 24, -8, y - 18, fur)
        hy = y - 38
    else:
        ph = st.get('phase', 0.0)
        s_ = math.sin(ph * math.pi)
        p.ell(-14, y - 22, -6, y - 14, fur_dk)
        p.ell(-12, y - 20, -8, y - 16, fur)
        p.ell(-12, y - 20, 10, y - 8, fur)
        for xx, sg in ((-9, 1), (-5, -1), (4, 1), (8, -1)):
            p.rect(xx + 2 * s_ * sg, y - 9, xx + 2 + 2 * s_ * sg, y, fur_dk if sg > 0 else fur)
        hy = y - 30
    p.ell(1, hy, 13, hy + 12, fur)
    p.poly([(9, hy + 5), (17, hy + 7), (16, hy + 11), (9, hy + 11)], lt)
    p.rect(16, hy + 6, 17, hy + 7, C['dark'])
    p.poly([(3, hy + 2), (4, hy - 5), (8, hy + 1)], fur_dk)
    p.poly([(7, hy + 1), (9, hy - 5), (11, hy + 2)], fur)
    p.rect(9, hy + 4, 10, hy + 4, C['dark'])
    if st.get('blink'):
        p.rect(9, hy + 4, 10, hy + 4, fur_dk)
    if st.get('mouth'):
        p.rect(13, hy + 10, 15, hy + 11, (200, 90, 90))


def draw_issun(d, x, y, f, st, t):
    """Issun-bōshi: about eight scene pixels tall.  st['boat'] draws his bowl and chopstick."""
    p = Pen(d, int(round(x)), f)
    y = int(round(y))
    if st.get('boat'):
        p.poly([(-7, y - 4), (7, y - 4), (5, y), (-5, y)], (180, 50, 44))
        p.rect(-7, y - 4, 7, y - 4, (220, 90, 70))
        a = math.sin(t * 4) * 3
        p.line([(3, y - 10), (9 + a, y + 1)], (220, 200, 160))
        y -= 3
    p.rect(-2, y - 6, 2, y - 1, (60, 90, 150))
    p.rect(-2, y - 3, 2, y - 3, (230, 200, 80))
    p.line([(-3, y - 4), (-6, y - 7)], (200, 204, 214))
    p.ell(-2, y - 11, 2, y - 6, SKIN)
    p.rect(-2, y - 12, 1, y - 10, HAIR)
    p.px(0, y - 13, HAIR)
    p.px(1, y - 9, C['dark'])
    if st.get('mouth'):
        p.px(2, y - 7, (120, 40, 40))


def draw_kasa(d, x, y, st, t):
    """Kasa-obake: an old paper umbrella with one eye, a long tongue and one leg."""
    x, y = int(round(x)), int(round(y))
    hop = st.get('hop', 0.0)
    y -= int(round(hop))
    paper, paper_dk = (176, 70, 90), (132, 48, 66)
    R(d, x - 1, y - 10, x + 1, y - 1, (226, 196, 160))           # leg
    for yy in range(y - 9, y - 2, 2):
        PX(d, x - 2, yy, (90, 60, 50))
    R(d, x - 4, y, x + 3, y + 1, (140, 100, 60))                 # geta
    R(d, x - 3, y + 2, x - 2, y + 2, (90, 60, 40))
    R(d, x + 1, y + 2, x + 2, y + 2, (90, 60, 40))
    PG(d, [(x - 3, y - 10), (x + 3, y - 10), (x + 10, y - 26), (x, y - 44), (x - 10, y - 26)], paper)
    PG(d, [(x, y - 10), (x + 3, y - 10), (x + 10, y - 26), (x, y - 44)], paper_dk)
    for k in (-6, -2, 3, 7):
        LN(d, [(x + k * 0.3, y - 11), (x + k, y - 27), (x, y - 43)], (110, 40, 56))
    R(d, x - 1, y - 48, x + 1, y - 44, (90, 60, 40))
    eye = st.get('eye', 'open')
    E(d, x - 5, y - 32, x + 4, y - 23, (250, 246, 236))
    if eye == 'open':
        E(d, x - 2, y - 29, x + 1, y - 26, C['dark'])
    else:
        LN(d, [(x - 4, y - 27), (x, y - 26), (x + 3, y - 27)], C['dark'])
    tl = st.get('tongue', 8)
    if tl:
        PG(d, [(x - 2, y - 21), (x + 2, y - 21), (x + 3, y - 21 + tl), (x, y - 19 + tl), (x - 2, y - 21 + tl * 0.7)],
           (224, 80, 90))


def draw_baku(d, x, y, f, st, t):
    """The baku, dream eater: tapir body, elephant trunk, tiger-striped legs, ox tail."""
    p = Pen(d, int(round(x)), f)
    y = int(round(y + math.sin(t * 1.6) * 1.5))
    body, body_dk, belly = (170, 170, 196), (130, 130, 160), (214, 214, 230)
    ph = st.get('phase', 0.0)
    s_ = math.sin(ph * math.pi)
    p.line([(-18, y - 20), (-24, y - 14), (-23, y - 8)], body_dk)
    p.ell(-25, y - 9, -21, y - 5, body_dk)
    for xx, sg in ((-14, 1), (-9, -1), (6, 1), (11, -1)):
        p.rect(xx + 2 * s_ * sg, y - 10, xx + 3 + 2 * s_ * sg, y, (232, 176, 80))
        p.rect(xx + 2 * s_ * sg, y - 7, xx + 3 + 2 * s_ * sg, y - 7, (60, 40, 30))
        p.rect(xx + 2 * s_ * sg, y - 3, xx + 3 + 2 * s_ * sg, y - 3, (60, 40, 30))
    p.ell(-19, y - 28, 15, y - 8, body)
    p.ell(-15, y - 18, 11, y - 9, belly)
    p.ell(8, y - 34, 24, y - 20, body)
    p.ell(10, y - 38, 15, y - 31, body_dk)
    reach = st.get('reach', 0.0)
    tx, ty = 22 + reach * 8, y - 26 - reach * 14
    p.line([(22, y - 26), (26 + reach * 4, y - 24 - reach * 6), (tx + 4, ty)], body, 3)
    p.line([(19, y - 22), (22, y - 18)], (240, 236, 220))
    if st.get('blink'):
        p.rect(16, y - 30, 18, y - 30, C['dark'])
    else:
        p.rect(17, y - 31, 18, y - 30, C['dark'])
    for (a, b_) in ((-12, y - 26), (-4, y - 27), (4, y - 26)):
        p.rect(a, b_, a + 3, b_, body_dk)


def draw_zashiki(d, sx, st, t):
    """Zashiki-warashi on a stool: a small child in red with a bobbed fringe, legs swinging."""
    dy = st.get('dy', 0)
    sw = math.sin(t * 3.1)
    body, body_dk = (196, 60, 60), (150, 40, 44)
    for s in (-1, 1):
        R(d, sx + s * 3 - 1, 138, sx + s * 3 + 1, 146 + int(sw * s), SKIN)
    PG(d, [(sx - 7, 120 + dy), (sx + 7, 120 + dy), (sx + 9, 138), (sx - 9, 138)], body)
    PG(d, [(sx + 5, 120 + dy), (sx + 7, 120 + dy), (sx + 9, 138), (sx + 6, 138)], body_dk)
    for (a, b) in ((-4, 126), (3, 130), (-2, 134)):
        PX(d, sx + a, b, (240, 200, 120))
    R(d, sx - 7, 130, sx + 7, 132, (240, 200, 120))
    hy = 106 + dy + st.get('hdy', 0)
    head = st.get('head', 'back')
    k = L(hair='bob', hair_c=HAIR)
    if head == 'back':
        R(d, sx - 2, hy + 10, sx + 1, hy + 13, SKIN_DK)
        E(d, sx - 6, hy, sx + 6, hy + 12, HAIR)
        R(d, sx - 6, hy + 5, sx + 6, hy + 11, HAIR)
    else:
        f = 1 if head == 'right' else -1
        p = Pen(d, sx, f)
        p.ell(-4, hy + 1, 5, hy + 12, SKIN)
        p.ell(-6, hy - 1, 4, hy + 10, HAIR)
        p.rect(-6, hy + 4, -1, hy + 11, HAIR)
        p.rect(0, hy + 1, 5, hy + 4, HAIR)
        p.rect(2, hy + 6, 3, hy + 7, C['dark'])
        p.rect(1, hy + 8, 2, hy + 8, C['blush'])
        p.rect(4, hy + 10, 4, hy + 10 + (1 if st.get('mouth') else 0), C['mouth'])


def draw_zashiki_walk(d, x, fy, f, st, t):
    p = Pen(d, int(round(x)), f)
    fy = int(round(fy))
    ph = st.get('phase', 0.0)
    s_ = math.sin(ph * math.pi)
    for sgn in (1, -1):
        p.rect(-3 + 2 * s_ * sgn, fy - 4, -1 + 2 * s_ * sgn, fy, SKIN)
    p.poly([(-5, fy - 26), (5, fy - 26), (7, fy - 4), (-7, fy - 4)], (196, 60, 60))
    p.rect(-6, fy - 15, 6, fy - 13, (240, 200, 120))
    hy = fy - 38
    p.ell(-4, hy + 1, 5, hy + 12, SKIN)
    p.ell(-6, hy - 1, 4, hy + 10, HAIR)
    p.rect(-6, hy + 4, -1, hy + 11, HAIR)
    p.rect(0, hy + 1, 5, hy + 4, HAIR)
    p.rect(2, hy + 6, 3, hy + 7, C['dark'])


def draw_okuni_dance(d, x, fy, st, t):
    """Okuni dancing: turns every beat, fan high."""
    beat = st.get('beat', 0.8)
    k = st['look']
    f = 1 if int(t / beat) % 2 == 0 else -1
    bob = 1 if (t % beat) < beat / 2 else 0
    draw_walker(d, x, fy - bob, f, k, dict(phase=0.0, mouth=st.get('mouth', 0)), t)
    p = Pen(d, int(round(x)), f)
    a = math.sin(t * 2 * math.pi / beat)
    tx, ty = 12 + 2 * a, fy - 66 - 4 * a
    p.poly([(9, fy - 40), (tx, ty), (tx + 8, ty - 6), (tx + 9, ty + 3)], (232, 70, 60))
    p.line([(tx, ty), (tx + 8, ty - 6)], (250, 220, 120))
