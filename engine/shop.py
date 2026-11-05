"""The ramen shop: the room, the counter, the wall of signed boards, lights, steam, the door
onto other worlds, and every character and prop placed by the director's state."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import cast as CS
from .gfx import (C, W, H, R, E, PG, PX, LN, Pen, FONT, SEATS, POT_X, clamp, ease, mix, shade, outline,
                  new_layer, glyph_mask)
from . import worlds

BOARD_SLOTS = [(7 + 7 * c, 14 + 9 * r) for r in range(5) for c in range(7)]
COUNTER_Y = 106


# ============================================================================ static scenery
def build_back():
    im = Image.new('RGB', (W, H), C['wall'])
    d = ImageDraw.Draw(im)
    rng = random.Random(3)
    for _ in range(1100):
        x, y = rng.randrange(W), rng.randrange(11, 146)
        PX(d, x, y, C['wall_dk'] if rng.random() < 0.65 else C['wall_hi'])
    R(d, 0, 0, W - 1, 3, C['ceiling'])
    R(d, 0, 4, W - 1, 9, C['beam'])
    R(d, 0, 4, W - 1, 4, C['beam_hi'])
    R(d, 0, 10, W - 1, 10, C['O'])
    for x0 in (0, 96, 315):
        R(d, x0, 11, x0 + 4, 146, C['post'])
        R(d, x0 + 1, 11, x0 + 1, 146, C['post_hi'])
    R(d, 0, 146, W - 1, H - 1, C['floor'])
    for i, y in enumerate(range(146, H, 6)):
        R(d, 0, y, W - 1, y, C['floor_ln'])
        off = (i * 23) % 40
        for x in range(off, W, 40):
            R(d, x, y + 1, x, min(H - 1, y + 5), C['floor_ln'])
    R(d, 100, 146, W - 1, 150, C['floor_dk'])
    R(d, 5, 121, 95, 145, C['wood_dk'])
    R(d, 5, 121, 95, 121, C['wood_hi'])
    for x in range(5, 96, 15):
        R(d, x, 122, x, 145, C['floor_ln'])
    # board rail above the door
    R(d, 5, 11, 55, 12, C['wood_dk'])
    R(d, 5, 58, 55, 59, C['wood_dk'])
    # door frame
    R(d, 5, 61, 55, 64, C['wood_dk'])
    R(d, 5, 61, 55, 61, C['wood_hi'])
    R(d, 6, 61, 9, 146, C['wood_dk'])
    R(d, 51, 61, 54, 146, C['wood_dk'])
    R(d, 7, 65, 7, 146, C['wood_hi'])
    R(d, 52, 65, 52, 146, C['wood_hi'])
    # window
    R(d, 56, 38, 94, 100, C['wood_dk'])
    R(d, 54, 99, 96, 102, C['wood_hi'])
    R(d, 54, 103, 96, 103, C['O'])
    # umbrella stand (the kasa-obake lives here)
    R(d, 60, 132, 70, 146, C['metal_dk'])
    R(d, 60, 132, 70, 133, C['metal'])
    LN(d, [(63, 132), (61, 112)], C['indigo'], 2)
    # kitchen tiles
    R(d, 244, 46, 314, 98, C['tile'])
    for y in range(48, 98, 6):
        R(d, 244, y, 314, y, C['tile_ln'])
        for x in range(244 + (y // 6 % 2) * 4, 315, 8):
            R(d, x, y, x, min(97, y + 5), C['tile_ln'])
    PG(d, [(240, 11), (314, 11), (314, 40), (246, 44)], C['metal_dk'])
    R(d, 246, 41, 314, 44, C['metal'])
    R(d, 246, 45, 314, 45, C['O'])
    for x in range(250, 312, 8):
        R(d, x, 14, x, 38, (88, 88, 100))
    # menu tags (one red special)
    for i, x in enumerate(range(104, 236, 11)):
        col = C['red'] if i == 4 else (216, 180, 122)
        ink = C['white'] if i == 4 else C['dark']
        R(d, x, 13, x + 8, 37, col)
        R(d, x, 13, x + 8, 13, C['O'])
        R(d, x, 37, x + 8, 37, C['O'])
        R(d, x, 13, x, 37, C['O'])
        R(d, x + 8, 13, x + 8, 37, C['O'])
        r2 = random.Random(i * 7 + 1)
        for k in range(3):
            yy = 16 + k * 7
            for _ in range(r2.randrange(2, 4)):
                if r2.random() < 0.5:
                    xa = x + 2 + r2.randrange(2)
                    R(d, xa, yy + r2.randrange(5), xa + r2.randrange(2, 4), yy + r2.randrange(5), ink)
                else:
                    xa = x + 2 + r2.randrange(5)
                    ya = yy + r2.randrange(2)
                    R(d, xa, ya, xa, ya + r2.randrange(2, 5), ink)
    for sy in (46, 68):
        R(d, 103, sy, 238, sy + 2, C['wood_hi'])
        R(d, 103, sy + 3, 238, sy + 3, C['O'])
        R(d, 103, sy + 4, 238, sy + 5, C['wall_dk'])

    def jar(x, y, w, h, c):
        R(d, x, y - h, x + w, y - 1, c)
        R(d, x + 1, y - h - 1, x + w - 1, y - h - 1, C['O'])
        R(d, x, y - h, x, y - 1, tuple(int(v * 0.75) for v in c))
        R(d, x + w, y - h, x + w, y - 1, C['O'])

    def bowls(x, y, n):
        for k in range(n):
            yy = y - 1 - k * 3
            R(d, x, yy - 2, x + 10, yy, C['bowl'])
            R(d, x, yy - 1, x + 10, yy - 1, C['red'])
            R(d, x, yy - 2, x + 10, yy - 2, C['bowl_dk'])
    jar(106, 46, 7, 10, (150, 96, 62))
    jar(115, 46, 6, 8, (120, 74, 50))
    bowls(124, 46, 3)
    bowls(137, 46, 4)
    E(d, 152, 36, 161, 45, C['red'])
    E(d, 154, 38, 159, 42, C['cream'])
    PX(d, 155, 40, C['dark'])
    PX(d, 158, 40, C['dark'])
    R(d, 152, 45, 161, 45, C['O'])
    jar(166, 46, 5, 16, (52, 88, 60))
    R(d, 167, 28, 170, 29, (210, 200, 170))
    jar(192, 46, 8, 7, (110, 120, 140))
    jar(203, 46, 6, 11, (150, 96, 62))
    bowls(212, 46, 2)
    jar(226, 46, 8, 9, (200, 190, 160))
    for k in range(4):
        R(d, 106, 66 - k * 2, 120, 67 - k * 2, C['bowl'] if k % 2 == 0 else C['bowl_dk'])
    for k, x in enumerate(range(126, 160, 6)):
        c = [(60, 40, 30), (90, 60, 30), (40, 60, 40)][k % 3]
        jar(x, 68, 3, 12 + (k % 2) * 3, c)
        R(d, x, 68 - 13 - (k % 2) * 3, x + 3, 68 - 13 - (k % 2) * 3, C['red'] if k % 2 else C['cream'])
    jar(166, 68, 14, 12, (210, 140, 160))
    R(d, 168, 59, 178, 59, C['cream'])
    PG(d, [(190, 67), (192, 54), (210, 54), (212, 67)], (214, 200, 160))
    R(d, 196, 58, 206, 62, C['red'])
    jar(218, 68, 7, 8, (150, 96, 62))
    jar(228, 68, 8, 11, (90, 110, 130))
    R(d, 104, 76, 160, 76, C['metal_dk'])
    for x in (108, 118, 130, 142, 152):
        LN(d, [(x, 76), (x, 88)], C['metal_hi'])
        E(d, x - 2, 88, x + 2, 92, C['metal'])
    # grandpa's note pinned by the hood: 雨の夜は誰にでも (rainy nights: feed whoever)
    R(d, 186, 74, 200, 92, C['paper'])
    R(d, 186, 74, 200, 74, C['O'])
    for yy in range(77, 91, 3):
        R(d, 189, yy, 197 - (yy % 5), yy, (80, 70, 70))
    R(d, 192, 73, 193, 74, C['red'])
    R(d, 100, 98, 314, 101, C['metal'])
    R(d, 100, 98, 314, 98, C['metal_hi'])
    R(d, 100, 102, 314, 105, C['metal_dk'])
    R(d, 263, 78, 297, 97, C['metal'])
    R(d, 268, 78, 270, 97, C['metal_hi'])
    R(d, 291, 78, 296, 97, C['metal_dk'])
    R(d, 259, 82, 262, 84, C['metal_dk'])
    R(d, 298, 82, 301, 84, C['metal_dk'])
    E(d, 262, 74, 298, 80, C['metal_hi'])
    E(d, 265, 75, 295, 79, (110, 70, 38))
    E(d, 268, 76, 292, 78, (140, 92, 50))
    LN(d, [(286, 77), (293, 62)], C['metal_hi'])
    LN(d, [(287, 77), (294, 62)], C['metal_dk'])
    R(d, 300, 86, 314, 97, C['metal_dk'])
    R(d, 300, 86, 314, 87, C['metal'])
    LN(d, [(303, 86), (301, 76)], C['metal_hi'])
    LN(d, [(309, 86), (311, 75)], C['metal_hi'])
    for k in range(3):
        R(d, 228, 95 - k * 3, 240, 97 - k * 3, C['bowl'])
        R(d, 228, 96 - k * 3, 240, 96 - k * 3, C['red'])
    R(d, 210, 95, 222, 97, C['wood_hi'])
    for x in range(211, 222, 2):
        PX(d, x, 95, C['onion'])
    return im


def build_maneki(d, wave):
    """The beckoning cat on the shelf; its paw waves."""
    E(d, 176, 37, 186, 45, C['white'])
    E(d, 177, 31, 185, 39, C['white'])
    PG(d, [(177, 33), (178, 29), (180, 32)], C['white'])
    PG(d, [(182, 32), (184, 29), (185, 33)], C['white'])
    PX(d, 179, 35, C['dark'])
    PX(d, 183, 35, C['dark'])
    R(d, 178, 39, 184, 39, C['red'])
    R(d, 185, 30 + wave, 187, 35 + wave, C['white'])
    PX(d, 181, 37, C['pink'])


def build_counter():
    im, d = new_layer()
    R(d, 100, 106, 319, 111, C['wood_top'])
    R(d, 100, 106, 319, 106, C['wood_hi'])
    R(d, 100, 111, 319, 112, C['wood_hi'])
    R(d, 100, 113, 319, 113, C['O'])
    R(d, 100, 114, 319, 145, C['wood'])
    for x in range(104, 320, 8):
        R(d, x, 114, x, 141, C['wood_dk'])
    R(d, 100, 114, 319, 115, C['wood_dk'])
    R(d, 100, 142, 319, 145, C['wood_dk'])
    R(d, 100, 106, 102, 145, C['wood_dk'])
    R(d, 99, 106, 99, 145, C['O'])
    R(d, 105, 98, 108, 107, (70, 40, 30))
    R(d, 105, 96, 108, 97, C['red'])
    R(d, 106, 99, 106, 105, (110, 70, 50))
    R(d, 111, 100, 114, 107, C['red_dk'])
    R(d, 111, 99, 114, 99, C['metal_hi'])
    PG(d, [(305, 99), (315, 99), (313, 107), (307, 107)], (176, 92, 60))
    for (x0, y0, x1, y1) in [(304, 90, 310, 97), (309, 86, 316, 95), (306, 92, 314, 99), (300, 93, 306, 99)]:
        E(d, x0, y0, x1, y1, (84, 140, 76))
    for (x, y) in [(306, 91), (311, 88), (313, 93)]:
        PX(d, x, y, (130, 186, 104))
    return outline(im)


def build_stools():
    im, d = new_layer()
    for x in SEATS:
        R(d, x - 1, 139, x + 1, 163, C['metal'])
        R(d, x + 1, 139, x + 1, 163, C['metal_dk'])
        E(d, x - 6, 150, x + 6, 154, C['metal_dk'])
        E(d, x - 5, 151, x + 5, 153, (0, 0, 0, 0))
        E(d, x - 6, 162, x + 6, 166, C['metal_dk'])
        R(d, x - 6, 164, x + 6, 164, C['metal'])
        E(d, x - 8, 133, x + 8, 140, C['red'])
        E(d, x - 7, 133, x + 6, 136, C['red_hi'])
        R(d, x - 7, 139, x + 7, 139, C['red_dk'])
    return outline(im)


def lantern_sprite(d, cx, top):
    R(d, cx - 1, 10, cx, top, C['O'])
    R(d, cx - 5, top, cx + 4, top + 2, C['lacquer'])
    E(d, cx - 9, top + 2, cx + 8, top + 23, (214, 70, 50))
    for k in range(5, 22, 3):
        R(d, cx - 8, top + k, cx + 7, top + k, (186, 54, 40))
    E(d, cx - 6, top + 4, cx - 2, top + 20, (236, 104, 74))
    R(d, cx - 5, top + 23, cx + 4, top + 25, C['lacquer'])
    ga = glyph_mask('麺')
    for yy, xx in zip(*np.nonzero(ga[1:15, 1:15])):
        PX(d, cx - 7 + xx, top + 5 + yy, (252, 236, 200))


# ============================================================================ moving parts
def bowl_sprite(d, cx, by, kind):
    p = Pen(d, cx)
    if kind in ('kitsune', 'shoyu', 'tsukimi', 'cold', 'miso'):
        if kind == 'kitsune':
            p.poly([(-8, by - 9), (-1, by - 11), (0, by - 8), (-7, by - 7)], C['tofu'])
            p.poly([(-1, by - 10), (7, by - 12), (8, by - 8), (0, by - 7)], C['tofu'])
            p.line([(-7, by - 9), (-2, by - 10)], C['tofu_dk'])
            p.line([(1, by - 9), (6, by - 10)], C['tofu_dk'])
            p.px(-1, by - 12, C['onion'])
            p.px(3, by - 13, C['onion'])
        elif kind == 'tsukimi':
            p.ell(-5, by - 11, 5, by - 6, C['egg'])
            p.ell(-2, by - 10, 2, by - 7, C['yolk'])
            p.px(5, by - 9, C['onion'])
            p.px(-6, by - 8, C['onion'])
        elif kind == 'cold':
            for k in range(-6, 7, 2):
                p.line([(k, by - 12), (k + 1, by - 7)], C['cucumber'])
            p.ell(-2, by - 11, 3, by - 8, C['yolk'])
            p.rect(-7, by - 9, -4, by - 8, C['pink'])
        else:
            p.rect(3, by - 15, 6, by - 7, C['nori'])
            p.ell(-7, by - 11, -1, by - 7, C['chashu'])
            p.rect(-6, by - 10, -3, by - 10, (226, 160, 132))
            p.ell(-1, by - 10, 3, by - 7, C['egg'])
            p.rect(0, by - 9, 1, by - 8, C['yolk'])
            p.ell(4, by - 10, 7, by - 7, C['naruto'])
            p.px(5, by - 9, C['pink'])
            p.px(-2, by - 8, C['onion'])
            p.px(2, by - 7, C['onion'])
    p.poly([(-8, by - 7), (8, by - 7), (7, by - 3), (4, by), (-4, by), (-7, by - 3)], C['bowl'])
    p.rect(-8, by - 7, 8, by - 7, C['white'] if kind != 'empty' else C['bowl_dk'])
    if kind == 'empty':
        p.rect(-6, by - 7, 6, by - 7, (200, 150, 100))
    for k in range(-6, 7, 2):
        p.px(k, by - 5, C['red'])
        p.px(k + 1, by - 4, C['red'])
    p.rect(-3, by, 3, by + 1, C['bowl_dk'])
    p.rect(4, by - 6, 6, by - 2, C['bowl_dk'])
    if kind == 'frozen':
        p.rect(-7, by - 9, 7, by - 7, (210, 230, 250))
        for k in (-5, -1, 3, 6):
            p.px(k, by - 10, (240, 250, 255))


def dog_bowl(d, x, y):
    E(d, x - 6, y - 3, x + 6, y + 1, (200, 60, 50))
    R(d, x - 5, y - 3, x + 5, y - 3, (230, 220, 200))


def draw_haru(d, s, t):
    cx, pose, mouth, blink = int(round(s['x'])), s['pose'], s.get('mouth', 0), s.get('blink', False)
    oy = s.get('oy', 0)
    if pose == 'walk':
        oy += 1 if (t * 5.5) % 2 < 1 else 0
    bow = 2 if pose == 'bow' else 0
    oy += bow
    if pose == 'back':
        _haru_back(d, cx, t, s.get('stir', True))
        return
    PG(d, [(cx - 10, 83 + oy), (cx + 10, 83 + oy), (cx + 12, 90 + oy), (cx + 12, 112), (cx - 12, 112), (cx - 12, 90 + oy)], C['indigo'])
    PG(d, [(cx + 8, 85 + oy), (cx + 10, 83 + oy), (cx + 12, 90 + oy), (cx + 12, 112), (cx + 9, 112)], C['indigo_dk'])
    PG(d, [(cx - 4, 83 + oy), (cx + 4, 83 + oy), (cx, 90 + oy)], C['cream'])
    LN(d, [(cx + 5, 83 + oy), (cx - 3, 96 + oy)], C['indigo_hi'])
    LN(d, [(cx - 5, 83 + oy), (cx - 1, 90 + oy)], C['indigo_hi'])
    if pose in ('carry', 'place', 'board'):
        for sgn in (-1, 1):
            R(d, cx + sgn * 11, 85 + oy, cx + sgn * 14, 95 + oy, C['indigo_dk'])
            R(d, cx + sgn * 8, 94 + oy, cx + sgn * 13, 97 + oy, C['skin_dk'])
        if pose == 'board':
            R(d, cx - 8, 86 + oy, cx + 8, 102 + oy, C['gold'])
            R(d, cx - 7, 87 + oy, cx + 7, 101 + oy, C['white'])
            if s.get('signed'):
                for yy in range(90 + oy, 99 + oy, 2):
                    R(d, cx - 2, yy, cx + 1, yy, C['dark'])
                R(d, cx + 3, 97 + oy, cx + 5, 99 + oy, C['red'])
            for sgn in (-1, 1):
                E(d, cx + sgn * 9 - 2, 94 + oy, cx + sgn * 9 + 2, 98 + oy, C['skin'])
        else:
            by = (97 if pose == 'carry' else 103) + oy
            bowl_sprite(d, cx, by, s.get('bowl') or 'shoyu')
            for sgn in (-1, 1):
                E(d, cx + sgn * 9 - 2, by - 5, cx + sgn * 9 + 2, by - 1, C['skin'])
    else:
        sw = 0
        if pose == 'walk':
            sw = 1 if (t * 5.5) % 2 < 1 else -1
        for sgn in (-1, 1):
            R(d, cx + sgn * 11, 85 + oy, cx + sgn * 14, 99 + oy + sw * sgn, C['indigo_dk'])
            R(d, cx + sgn * 12, 100 + oy + sw * sgn, cx + sgn * 14, 110, C['skin'])
    R(d, cx - 2, 78 + oy, cx + 1, 83 + oy, C['skin_dk'])
    hy = oy + bow
    E(d, cx - 8, 61 + hy, cx + 7, 79 + hy, C['hair'])
    E(d, cx - 6, 64 + hy, cx + 5, 80 + hy, C['skin'])
    E(d, cx - 8, 59 + hy, cx + 7, 70 + hy, C['hair'])
    R(d, cx - 8, 67 + hy, cx - 7, 78 + hy, C['hair'])
    R(d, cx + 6, 67 + hy, cx + 7, 78 + hy, C['hair'])
    for x in range(cx - 6, cx + 5, 3):
        PG(d, [(x, 69 + hy), (x + 3, 69 + hy), (x + 1, 71 + hy)], C['hair'])
    R(d, cx - 8, 65 + hy, cx + 7, 66 + hy, C['white'])
    R(d, cx - 8, 67 + hy, cx - 4, 67 + hy, C['white'])
    R(d, cx + 7, 63 + hy, cx + 9, 67 + hy, C['white'])
    PG(d, [(cx + 9, 66 + hy), (cx + 12, 71 + hy), (cx + 10, 71 + hy), (cx + 8, 67 + hy)], C['white'])
    if blink or pose == 'bow':
        R(d, cx - 4, 74 + hy, cx - 3, 74 + hy, C['dark'])
        R(d, cx + 1, 74 + hy, cx + 2, 74 + hy, C['dark'])
    else:
        lx = s.get('look', 0)
        R(d, cx - 4 + lx, 72 + hy, cx - 3 + lx, 74 + hy, C['dark'])
        R(d, cx + 1 + lx, 72 + hy, cx + 2 + lx, 74 + hy, C['dark'])
        PX(d, cx - 4 + lx, 72 + hy, (120, 110, 130))
        PX(d, cx + 1 + lx, 72 + hy, (120, 110, 130))
    R(d, cx - 6, 76 + hy, cx - 5, 76 + hy, C['blush'])
    R(d, cx + 3, 76 + hy, cx + 4, 76 + hy, C['blush'])
    if mouth:
        R(d, cx - 1, 77 + hy, cx, 78 + hy, (110, 40, 40))
        PX(d, cx, 78 + hy, C['pink'])
    else:
        R(d, cx - 1, 78 + hy, cx, 78 + hy, C['mouth'])
        PX(d, cx - 2, 77 + hy, C['mouth'])
        PX(d, cx + 1, 77 + hy, C['mouth'])


def _haru_back(d, cx, t, stir):
    PG(d, [(cx - 10, 83), (cx + 10, 83), (cx + 12, 90), (cx + 12, 112), (cx - 12, 112), (cx - 12, 90)], C['indigo'])
    PG(d, [(cx - 10, 83), (cx - 8, 85), (cx - 9, 112), (cx - 12, 112), (cx - 12, 90)], C['indigo_dk'])
    R(d, cx - 14, 85, cx - 11, 104, C['indigo_dk'])
    R(d, cx - 14, 105, cx - 12, 110, C['skin_dk'])
    a = t * 4.2 if stir else 0
    ex, ey = 3 * math.cos(a), 2 * math.sin(a)
    LN(d, [(cx + 11, 86), (cx + 15 + ex, 92 + ey)], C['indigo_dk'], 4)
    LN(d, [(cx + 8 + ex, 80 + ey), (cx + 13 + ex, 66 + ey)], C['metal_hi'], 1)
    R(d, cx - 2, 77, cx + 1, 83, C['skin_dk'])
    E(d, cx - 8, 59, cx + 7, 79, C['hair'])
    R(d, cx - 8, 65, cx + 7, 66, C['white'])
    R(d, cx - 1, 64, cx + 1, 67, C['white'])
    R(d, cx + 2, 66, cx + 3, 71, C['white'])
    R(d, cx + 1, 66, cx + 1, 69, C['white'])
    R(d, cx - 6, 70, cx + 5, 70, C['hair'])


def draw_cho(d, s, t):
    sway = s.get('sway', 0.0)
    cx = 75 + int(round(sway))
    top = 13
    R(d, 75, 10, 75, top, C['O'])
    R(d, cx - 4, top, cx + 4, top + 2, C['lacquer'])
    E(d, cx - 7, top + 2, cx + 7, top + 21, C['paper'])
    for k in range(5, 20, 3):
        R(d, cx - 6, top + k, cx + 6, top + k, C['paper_dk'])
    R(d, cx - 4, top + 21, cx + 4, top + 23, C['lacquer'])
    eye = s.get('eye', 'closed')
    ey = top + 8
    if eye in ('open', 'wide'):
        r = 3 if eye == 'wide' else 2
        E(d, cx - r - 1, ey - r, cx + r, ey + r, (255, 252, 240))
        R(d, cx - r - 1, ey - r - 1, cx + r, ey - r - 1, C['dark'])
        lx, ly = s.get('look', (0, 0))
        R(d, cx - 1 + lx, ey - 1 + ly, cx + lx, ey + ly, C['dark'])
    elif eye == 'wink':
        LN(d, [(cx - 3, ey + 1), (cx - 1, ey - 1), (cx + 2, ey + 1)], C['dark'])
    else:
        LN(d, [(cx - 3, ey), (cx - 1, ey + 1), (cx + 2, ey)], C['dark'])
    if s.get('talk'):
        E(d, cx - 4, top + 13, cx + 4, top + 18, (110, 40, 40))
        R(d, cx - 2, top + 16, cx + 2, top + 17, (222, 76, 84))
    else:
        R(d, cx - 5, top + 15, cx + 5, top + 15, C['dark'])
    if s.get('tongue'):
        PG(d, [(cx - 1, top + 16), (cx + 2, top + 16), (cx + 2, top + 22), (cx, top + 24), (cx - 1, top + 21)], (222, 76, 84))


def draw_door(d, s):
    o, rattle = s['open'], s.get('rattle', 0)
    x_right = int(round(50 - 40 * o)) + rattle
    if x_right >= 10:
        R(d, 10, 66, x_right, 145, C['wood_dk'])
        R(d, 11, 68, x_right - 1, 117, (92, 104, 140))
        for x in range(13, x_right, 5):
            R(d, x, 68, x, 118, C['wood'])
        for y in (80, 94, 106):
            R(d, 10, y, x_right, y, C['wood'])
        R(d, 10, 118, x_right, 145, C['wood'])
        R(d, 10, 118, x_right, 118, C['wood_hi'])
        R(d, 10, 66, x_right, 67, C['wood_hi'])
        if x_right > 12:
            R(d, x_right - 1, 66, x_right, 145, C['wood_dk'])
    return x_right


def draw_noren(d, s, t):
    lift = s.get('lift', [0, 0, 0])
    if s.get('down'):
        return
    R(d, 9, 64, 51, 65, C['wood_dk'])
    panels = [(10, 22), (24, 36), (38, 50)]
    for i, (x0, x1) in enumerate(panels):
        sway = math.sin(t * 1.3 + i) * 0.6 + s.get('gust', 0) * math.sin(t * 9 + i)
        bottom = 88 - int(round(lift[i]))
        PG(d, [(x0, 66), (x1, 66), (x1 + sway, bottom), (x0 + sway, bottom)], C['indigo'])
        R(d, x0, 66, x1, 67, C['indigo_dk'])
    if lift[1] < 8:
        E(d, 25, 71, 35, 81, C['white'])
        LN(d, [(30, 76), (32, 75), (32, 78), (28, 78), (27, 74), (31, 72), (34, 74)], C['pink'])


def draw_board_slot(d, i, color, glow=0.0):
    x, y = BOARD_SLOTS[i]
    R(d, x, y, x + 5, y + 7, C['gold'] if glow <= 0 else mix(C['gold'], (255, 250, 220), glow))
    R(d, x + 1, y + 1, x + 4, y + 6, C['white'])
    R(d, x + 2, y + 2, x + 3, y + 4, color)
    PX(d, x + 4, y + 6, C['red'])


# ============================================================================ props
def draw_prop(d, pr, t):
    n = pr['name']
    x = pr.get('x', 0)
    if n == 'notebook':
        R(d, x - 7, 104, x + 6, 107, (240, 236, 226))
        R(d, x - 7, 104, x + 6, 104, (120, 160, 210))
        for xx in range(x - 5, x + 5, 3):
            PX(d, xx, 106, (90, 90, 120))
    elif n == 'cards':
        for i in range(3):
            R(d, x - 5 + i * 3, 104 - i, x + 1 + i * 3, 107 - i, (250, 250, 244))
            R(d, x - 5 + i * 3, 104 - i, x + 1 + i * 3, 104 - i, (230, 90, 80))
    elif n == 'box':
        o = pr.get('open', 0.0)
        R(d, x - 6, 98, x + 6, 107, (40, 30, 34))
        R(d, x - 6, 102, x + 6, 102, (200, 60, 50))
        R(d, x - 1, 98, x + 1, 107, (200, 60, 50))
        lid = int(o * 6)
        R(d, x - 7, 96 - lid, x + 7, 98 - lid, (54, 40, 44))
        if o > 0.2:
            for k in range(3):
                E(d, x - 3 + k * 3, 90 - lid - k * 3, x + 1 + k * 3, 94 - lid - k * 3, (240, 240, 250))
    elif n == 'elekiter':
        R(d, x - 7, 96, x + 7, 107, (150, 90, 50))
        R(d, x - 7, 96, x + 7, 97, (190, 130, 80))
        for xx in range(x - 5, x + 6, 3):
            PX(d, xx, 101, (240, 220, 140))
        LN(d, [(x + 7, 100), (x + 11, 98)], (90, 70, 50))
        a = t * 8 if pr.get('crank') else 0
        LN(d, [(x + 11, 98), (x + 11 + 3 * math.cos(a), 98 + 3 * math.sin(a))], (200, 200, 210))
        LN(d, [(x - 3, 96), (x - 3, 90)], (200, 180, 120))
        if pr.get('spark') and (t * 12) % 2 < 1:
            LN(d, [(x - 3, 90), (x - 6, 86), (x - 2, 84), (x - 5, 80)], (220, 240, 255))
    elif n == 'oar':
        LN(d, [(x - 14, 106), (x + 14, 103)], (176, 136, 86), 2)
        if pr.get('shavings'):
            for k in range(4):
                PX(d, x - 4 + k * 3, 107, (220, 190, 140))
    elif n == 'plum':
        LN(d, [(x - 8, 106), (x + 6, 101), (x + 10, 97)], (90, 60, 40))
        for (a, b) in ((6, 100), (10, 96), (2, 103), (-3, 104)):
            PX(d, x + a, b - 1, (250, 170, 190))
            PX(d, x + a + 1, b - 1, (255, 220, 230))
    elif n == 'paper':
        R(d, x - 10, 104, x + 10, 107, (246, 240, 224))
        if pr.get('wave'):
            k = pr['wave']
            pts = [(x - 9 + i * 2, 106 - (2 if i % 4 == 1 else 0) - (1 if i % 4 == 2 else 0)) for i in range(int(10 * k))]
            if len(pts) > 1:
                LN(d, pts, (60, 90, 150))
    elif n == 'cup':
        R(d, x - 2, 101, x + 2, 107, (200, 196, 180))
        R(d, x - 2, 101, x + 2, 101, (120, 160, 100) if not pr.get('frozen') else (220, 240, 255))
    elif n == 'stack':
        nb = int(pr.get('n', 0))
        cols = [x + i * 13 for i in range(max(1, (nb + 7) // 8))]
        k = 0
        for cxx in cols:
            for j in range(8):
                if k >= nb:
                    break
                yy = 105 - j * 4
                R(d, cxx - 5, yy - 3, cxx + 5, yy, C['bowl'])
                R(d, cxx - 5, yy - 1, cxx + 5, yy - 1, C['red'])
                R(d, cxx - 5, yy - 3, cxx + 5, yy - 3, C['bowl_dk'])
                k += 1
    elif n == 'party':
        for i, xx in enumerate(range(104, 312, 9)):
            yy = 12 + int(3 * math.sin(i * 0.9))
            col = ((240, 90, 80), (250, 200, 80), (120, 200, 120), (110, 160, 240))[i % 4]
            PG(d, [(xx, yy), (xx + 6, yy), (xx + 3, yy + 6)], col)
        LN(d, [(104, 12), (312, 12)], (60, 40, 40))
    elif n == 'bubble':
        bx, by, k = int(pr['x']), int(pr['y']), pr.get('k', 1.0)
        if k <= 0:
            return
        r = 12 * k
        for (dx, dy_, rr) in ((-r * 0.9, 0, r * 0.7), (0, -r * 0.3, r), (r * 0.9, 0, r * 0.7), (0, r * 0.35, r * 0.75)):
            E(d, bx + dx - rr, by + dy_ - rr * 0.8, bx + dx + rr, by + dy_ + rr * 0.8, (236, 230, 246))
        E(d, bx - 13 * k - 3, by + 14 * k, bx - 13 * k + 1, by + 14 * k + 3, (236, 230, 246))
        E(d, bx - 17 * k - 2, by + 19 * k, bx - 17 * k, by + 19 * k + 2, (236, 230, 246))
        if k > 0.6:
            R(d, bx - 6, by - 7, bx + 4, by + 6, (250, 250, 244))
            for yy in range(by - 5, by + 5, 3):
                R(d, bx - 4, yy, bx + 2, yy, (160, 160, 170))
            for (a, b) in ((2, -2), (3, -1), (4, 0), (3, 1), (2, 2)):
                PX(d, bx + a + 2, by + b + 1, (220, 40, 40))
            R(d, bx + 2, by - 3, bx + 2, by + 3, (220, 40, 40))
            R(d, bx + 2, by - 3, bx + 5, by - 3, (220, 40, 40))
            R(d, bx + 2, by, bx + 4, by, (220, 40, 40))
    elif n == 'smoke':
        k = pr.get('k', 1.0)
        for i in range(7):
            a = i * 0.9 + t * 3
            rr = 3 + 5 * k
            ox, oy = math.cos(a) * 8 * k, math.sin(a) * 5 * k
            E(d, pr['x'] + ox - rr, pr['y'] + oy - rr, pr['x'] + ox + rr, pr['y'] + oy + rr, (236, 232, 228))
    elif n == 'needle':
        LN(d, [(x - 3, 106), (x + 3, 105)], (210, 214, 224))
    elif n == 'leaf':
        PG(d, [(x - 3, pr['y']), (x, pr['y'] - 3), (x + 3, pr['y']), (x, pr['y'] + 2)], (90, 160, 70))


def draw_char(d, s, t, castmap):
    who = s['who']
    spec = castmap[who]
    kind = spec['kind']
    k = spec.get('look')
    if kind == 'kon':
        CS.draw_kon(d, s, t)
        return
    if s.get('variant') == 'kettle':
        CS.draw_kettle(d, s['x'], t, s.get('wobble', 0.0))
        return
    mode = s['mode']
    if kind == 'dog':
        CS.draw_dog(d, s['x'], s.get('y', 166), s.get('f', -1), s, t)
    elif kind == 'issun':
        CS.draw_issun(d, s['x'], s.get('y', 106), s.get('f', 1), s, t)
    elif kind == 'kasa':
        CS.draw_kasa(d, s['x'], s.get('y', 146), s, t)
    elif kind == 'baku':
        CS.draw_baku(d, s['x'], s.get('y', 170), s.get('f', 1), s, t)
    elif kind == 'zashiki':
        if mode == 'sit':
            CS.draw_zashiki(d, s['x'], s, t)
        else:
            CS.draw_zashiki_walk(d, s['x'], s.get('y', 170), s.get('f', 1), s, t)
    else:
        kk = k
        extra = {kx: s[kx] for kx in ('paper', 'spilled', 'hat_off') if s.get(kx)}
        if extra:
            kk = CS.Look(k)
            kk.update(extra)
            if extra.get('hat_off'):
                kk['hat'] = None
        if mode == 'sit':
            CS.draw_seated(d, s['x'], kk, s, t)
        elif mode == 'dance':
            CS.draw_okuni_dance(d, s['x'], s.get('y', 170), dict(s, look=kk), t)
        else:
            CS.draw_walker(d, s['x'], s.get('y', 170), s.get('f', 1), kk, s, t)


# ============================================================================ the scene
class Shop:
    def __init__(self, castmap):
        self.castmap = castmap
        self.back = np.asarray(build_back()).astype(np.float32) / 255.0
        self.counter = build_counter()
        self.stools = build_stools()
        m = np.zeros((H, W), bool)
        m[40:99, 58:93] = True
        m[40:99, 74:76] = False
        m[68:70, 58:93] = False
        self.win_mask = m
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.yy, self.xx = yy, xx
        self.lights = {}
        for name, (lx, ly, r) in dict(lanA=(128, 26, 72), lanB=(214, 26, 72), cho=(75, 24, 38), hood=(282, 52, 46),
                                      window=(75, 70, 30), door=(30, 112, 44), door_in=(30, 150, 30)).items():
            dist2 = (xx - lx) ** 2 + ((yy - ly) * 1.15) ** 2
            self.lights[name] = 1.0 / (1.0 + dist2 / (r * r))
        self.lcol = dict(lanA=(1.0, 0.62, 0.38), lanB=(1.0, 0.62, 0.38), cho=(1.0, 0.80, 0.50), hood=(1.0, 0.86, 0.64),
                         window=(0.40, 0.50, 0.85), door=(0.42, 0.54, 0.90), door_in=(0.42, 0.54, 0.90))
        b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0
        self.bayer = np.tile(b, (H // 4 + 1, W // 4 + 1))[:H, :W][:, :, None]
        em, d = new_layer()
        lantern_sprite(d, 128, 12)
        lantern_sprite(d, 214, 12)
        LN(d, [(248, 46), (312, 46)], (255, 236, 190))
        self.lanterns = outline(em)
        la = np.asarray(self.lanterns).astype(np.float32) / 255.0
        self.lan_rgb, self.lan_a = la[:, :, :3], la[:, :, 3:4]
        g = Image.fromarray((la[:, :, :3] * la[:, :, 3:4] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
        self.glow = np.asarray(g).astype(np.float32) / 255.0
        self._dyn = {}

    def _dynlight(self, x, y, r):
        key = (int(x), int(y), int(r))
        if key not in self._dyn:
            dist2 = (self.xx - x) ** 2 + ((self.yy - y) * 1.15) ** 2
            self._dyn[key] = 1.0 / (1.0 + dist2 / (r * r))
        return self._dyn[key]

    def lightmap(self, t, st):
        door_open = st['door']['open']
        fl = 1.0 + 0.035 * math.sin(t * 7.1) + 0.025 * math.sin(t * 13.3 + 1.0)
        fl2 = 1.0 + 0.035 * math.sin(t * 6.3 + 2.0) + 0.025 * math.sin(t * 11.7)
        k = dict(lanA=1.05 * fl, lanB=1.05 * fl2, cho=0.55 * fl2, hood=0.95, window=0.45,
                 door=0.85 * door_open, door_in=0.5 * door_open)
        Lm = np.empty((H, W, 3), np.float32)
        amb = (0.26, 0.21, 0.24) if st.get('weather') != 'snow' else (0.25, 0.23, 0.28)
        Lm[:] = amb
        for n, m in self.lights.items():
            if k[n] > 0:
                Lm += m[:, :, None] * (np.array(self.lcol[n], np.float32) * k[n])
        for (lx, ly, r, col, kk) in st.get('lights', ()):
            if kk > 0:
                Lm += self._dynlight(lx, ly, r)[:, :, None] * (np.array(col, np.float32) * kk)
        Lm = np.floor(Lm * 10.0 + self.bayer) / 10.0
        return Lm, fl

    def render(self, st, t):
        """State dict -> 320x180 RGB float image."""
        est = st.get('establish')
        if est and est.get('a', 0) >= 1.0:
            v = np.asarray(worlds.view(est['view'], t, st.get('weather', 'rain'))).astype(np.float32) / 255.0
            return v
        img = self._render_shop(st, t)
        if est and est.get('a', 0) > 0:
            v = np.asarray(worlds.view(est['view'], t, st.get('weather', 'rain'))).astype(np.float32) / 255.0
            a = est['a']
            img = img * (1 - a) + v * a
        return img

    def _render_shop(self, st, t):
        alb = self.back.copy()
        unlit = np.zeros((H, W), bool)
        door = st['door']
        weather = st.get('weather', 'rain')
        # window: our own street, today
        wv = np.zeros((H, W, 3), np.float32)
        street = worlds.view('street', t, weather).crop((96, 30, 206, 180))
        wv[30:180, 0:110] = np.asarray(street).astype(np.float32)[:150] / 255.0
        m = self.win_mask
        alb[m] = wv[m]
        unlit |= m
        # back-wall dynamic bits: boards, maneki-neko
        bl, bd = new_layer()
        for i, (col, glow) in enumerate(st.get('boards', ())):
            draw_board_slot(bd, i, col, glow)
        wave = 1 if st.get('maneki', 0) and (t * 3) % 2 < 1 else 0
        build_maneki(bd, -wave)
        layers = [bl]
        # door and what is outside it
        dl, dd = new_layer()
        xr = draw_door(dd, door)
        if xr < 50:
            crop = worlds.door_crop(door.get('outside', 'street'), t, weather)
            v = np.zeros((H, W, 3), np.float32)
            v[66:146, 10:51] = np.asarray(crop).astype(np.float32) / 255.0
            dm = np.zeros((H, W), bool)
            dm[66:146, max(10, xr + 1):51] = True
            alb[dm] = v[dm]
            unlit |= dm
            for c in st['chars']:
                if c.get('outside'):
                    lay, d = new_layer()
                    draw_char(d, c, t, self.castmap)
                    a = np.asarray(outline(lay)).copy()
                    clip = np.zeros((H, W), bool)
                    clip[66:146, max(10, xr + 1):51] = True
                    a[~clip] = 0
                    layers.append(Image.fromarray(a, 'RGBA'))
        layers.append(dl)
        lay, d = new_layer()
        draw_haru(d, st['haru'], t)
        layers.append(outline(lay))
        layers.append(self.counter)
        lay, d = new_layer()
        for b in st.get('bowls', ()):
            if b.get('floor'):
                continue
            bowl_sprite(d, b['x'], 108, b['kind'])
        for pr in st.get('props', ()):
            if pr['name'] not in ('party', 'bubble', 'smoke', 'leaf'):
                draw_prop(d, pr, t)
        for c in st['chars']:
            if c.get('on_counter'):
                draw_char(d, c, t, self.castmap)
        layers.append(outline(lay))
        layers.append(self.stools)
        floor_items = []
        for b in st.get('bowls', ()):
            if b.get('floor'):
                floor_items.append(b)
        if floor_items:
            lay, d = new_layer()
            for b in floor_items:
                dog_bowl(d, b['x'], b.get('y', 168))
            layers.append(outline(lay))
        if st.get('staff'):
            lay, d = new_layer()
            for (sx_, kind) in st['staff']:
                if kind == 'spear':
                    LN(d, [(sx_ + 16, 166), (sx_ + 22, 72)], (110, 80, 50), 1)
                    PG(d, [(sx_ + 22, 64), (sx_ + 24, 72), (sx_ + 20, 72)], (200, 200, 210))
                else:
                    LN(d, [(sx_ + 16, 166), (sx_ + 22, 92)], (126, 92, 60), 2)
            layers.append(outline(lay))
        seated = [c for c in st['chars'] if c['mode'] == 'sit' and not c.get('outside') and not c.get('on_counter')]
        for c in sorted(seated, key=lambda c: c['x']):
            lay, d = new_layer()
            draw_char(d, c, t, self.castmap)
            layers.append(outline(lay))
        if st.get('hat_stool'):
            lay, d = new_layer()
            x = st['hat_stool']
            PG(d, [(x - 12, 135), (x - 5, 129), (x, 128), (x + 5, 129), (x + 12, 135), (x, 136)], (212, 178, 108))
            LN(d, [(x - 8, 133), (x, 130), (x + 8, 133)], (166, 130, 74))
            layers.append(outline(lay))
        walkers = [c for c in st['chars'] if c['mode'] != 'sit' and not c.get('outside') and not c.get('on_counter')]
        lay, d = new_layer()
        draw_noren(d, st['noren'], t)
        noren_layer = outline(lay)
        for c in sorted(walkers, key=lambda c: c.get('y', 170)):
            if c.get('y', 170) < 150:
                lay, d = new_layer()
                draw_char(d, c, t, self.castmap)
                layers.append(outline(lay))
        layers.append(noren_layer)
        for c in sorted(walkers, key=lambda c: c.get('y', 170)):
            if c.get('y', 170) >= 150:
                lay, d = new_layer()
                draw_char(d, c, t, self.castmap)
                layers.append(outline(lay))
        fx = [pr for pr in st.get('props', ()) if pr['name'] in ('party', 'bubble', 'smoke', 'leaf')]
        if fx:
            lay, d = new_layer()
            for pr in fx:
                draw_prop(d, pr, t)
            layers.append(outline(lay) if any(p['name'] != 'smoke' for p in fx) else lay)
        for lay in layers:
            a = np.asarray(lay)
            msk = a[:, :, 3] > 0
            alb[msk] = a[:, :, :3][msk].astype(np.float32) / 255.0
            unlit[msk] = False
        Lm, fl = self.lightmap(t, st)
        out = np.where(unlit[:, :, None], alb, alb * Lm)
        out = out * (1 - self.lan_a) + self.lan_rgb * self.lan_a
        out += self.glow * (0.55 * fl)
        if any(p['name'] == 'party' for p in st.get('props', ())):
            out = self._party_bulbs(out, t)
        cl, cd = new_layer()
        draw_cho(cd, st['cho'], t)
        ca = np.asarray(outline(cl)).astype(np.float32) / 255.0
        out = out * (1 - ca[:, :, 3:4]) + ca[:, :, :3] * ca[:, :, 3:4]
        out = self.steam(out, st, t)
        if door['open'] > 0.3 and weather == 'snow' or st.get('snowgust'):
            out = self._snow_in(out, t, max(door['open'], st.get('snowgust', 0)))
        if st.get('flash', 0) > 0:
            out = out + st['flash'] * 0.55
        if st.get('dim', 0) > 0:
            out = out * (1 - 0.55 * st['dim'])
        return np.clip(out, 0, 1)

    def _party_bulbs(self, out, t):
        for i, x in enumerate(range(108, 312, 12)):
            y = 18 + int(2 * math.sin(i * 1.3))
            on = (int(t * 2) + i) % 3 != 0
            col = np.array(((1.0, 0.85, 0.5), (1.0, 0.6, 0.6), (0.6, 1.0, 0.7))[i % 3], np.float32)
            if on:
                out[y:y + 2, x:x + 2] = col
                out[max(0, y - 3):y + 5, max(0, x - 3):x + 5] += col * 0.08
        return out

    def _snow_in(self, out, t, k):
        rng = random.Random(21)
        for i in range(int(40 * k)):
            x0, y0, sp = rng.uniform(10, 60), rng.uniform(60, 170), rng.uniform(10, 30)
            x = x0 + (t * sp) % 90
            y = y0 + 6 * math.sin(t * 2 + i)
            if 0 <= x < W and 0 <= y < H:
                out[int(y), int(x)] = (0.95, 0.96, 1.0)
        return out

    def steam(self, out, st, t):
        srcs = [(281, 74, 1.0, 20)]
        for b in st.get('bowls', ()):
            if b.get('steam', 0) > 0 and not b.get('floor'):
                srcs.append((b['x'], 94, b['steam'], 7))
        if st['haru']['pose'] in ('carry', 'place'):
            srcs.append((st['haru']['x'], 84, 0.7, 6))
        ov = np.zeros((H, W), np.float32)
        for si, (sx, sy, k, n) in enumerate(srcs):
            rng = random.Random(si * 31 + int(sx))
            life = 2.6
            for i in range(n):
                ph, amp, sp = rng.uniform(0, life), rng.uniform(1.5, 4.0), rng.uniform(9, 14)
                age = (t + ph) % life
                y = sy - age * sp
                x = sx + rng.uniform(-3, 3) + math.sin(age * 2.2 + i) * amp * (age / life + 0.3)
                a = 0.38 * k * math.sin(math.pi * age / life)
                xi, yi = int(round(x)), int(round(y))
                for dx, dy in ((0, 0), (1, 0), (0, -1), (1, -1)):
                    if 0 <= xi + dx < W and 0 <= yi + dy < H:
                        ov[yi + dy, xi + dx] = max(ov[yi + dy, xi + dx], a)
        col = np.array([0.96, 0.92, 0.86], np.float32)
        return out * (1 - ov[:, :, None]) + col * ov[:, :, None]
