"""The worlds outside the door.  Each view is a 320x180 picture used two ways: whole, as a
short establishing shot ("Edo, 1689"), and cropped through the open door (a 41x80 hole)."""
import math
import random

from PIL import Image, ImageDraw

from .gfx import R, E, PG, PX, LN, mix, shade

VW, VH = 320, 180


def sky(d, top, bot, y0=0, y1=VH):
    for y in range(y0, y1):
        u = (y - y0) / max(1, (y1 - y0 - 1))
        R(d, 0, y, VW - 1, y, mix(top, bot, u))


def moon(d, x, y, r, c=(250, 240, 200), glow=(60, 70, 110)):
    for k, a in ((2.4, 0.18), (1.7, 0.35)):
        E(d, x - r * k, y - r * k, x + r * k, y + r * k, mix(glow, c, a * 0.4))
    E(d, x - r, y - r, x + r, y + r, c)
    E(d, x - r * 0.4, y - r * 0.5, x - r * 0.1, y - r * 0.2, shade(c, 0.93))


def ridge(d, pts, c, base=VH):
    PG(d, [(0, base)] + pts + [(VW, base)], c)


def stars(d, seed, n, ymax, c=(220, 220, 240)):
    rng = random.Random(seed)
    for _ in range(n):
        PX(d, rng.randrange(VW), rng.randrange(ymax), c)


def pine(d, x, y, s=1.0, c=(26, 52, 44), hi=(38, 70, 56), trunk=(40, 30, 30)):
    R(d, x - 1, y - 60 * s, x + 2, y, trunk)
    for (dx0, dy0, w, h) in ((-14, -60, 28, 10), (-6, -50, 32, 10), (-18, -38, 28, 10), (-6, -24, 24, 8)):
        E(d, x + dx0 * s, y + dy0 * s, x + (dx0 + w) * s, y + (dy0 + h) * s, c)
        R(d, x + (dx0 + 3) * s, y + (dy0 + 2) * s, x + (dx0 + w - 3) * s, y + (dy0 + 3) * s, hi)


def stone_lantern(d, x, y, lit=True):
    R(d, x - 3, y - 10, x + 3, y - 8, (110, 110, 104))
    R(d, x - 1, y - 7, x + 1, y, (100, 100, 96))
    R(d, x - 2, y - 15, x + 2, y - 11, (120, 118, 110))
    PG(d, [(x - 5, y - 15), (x, y - 20), (x + 5, y - 15)], (100, 100, 96))
    if lit:
        PX(d, x, y - 13, (255, 196, 110))


def chochin(d, x, y, c=(214, 70, 50)):
    E(d, x - 3, y, x + 3, y + 7, c)
    R(d, x - 2, y - 1, x + 2, y - 1, (40, 30, 30))
    R(d, x - 2, y + 8, x + 2, y + 8, (40, 30, 30))
    PX(d, x - 1, y + 2, mix(c, (255, 230, 180), 0.5))


def wood_house(d, x0, x1, ybase, h, roof=(46, 40, 48), wall=(84, 62, 48), lit=True, seed=0):
    rng = random.Random(seed)
    PG(d, [(x0 - 4, ybase - h), (x1 + 4, ybase - h), (x1, ybase - h - 8), (x0, ybase - h - 8)], roof)
    R(d, x0, ybase - h, x1, ybase, wall)
    for x in range(x0 + 3, x1, 5):
        R(d, x, ybase - h + 2, x, ybase, shade(wall, 0.8))
    if lit:
        for _ in range(max(1, (x1 - x0) // 22)):
            wx = rng.randrange(x0 + 2, max(x0 + 3, x1 - 12))
            R(d, wx, ybase - h + 5, wx + 9, ybase - h + 13, (226, 168, 92))
            for xx in range(wx + 3, wx + 9, 3):
                R(d, xx, ybase - h + 5, xx, ybase - h + 13, (176, 120, 66))


def rain(d, t, seed, c, n, w=VW, h=VH, slant=0.3, speed=(220, 280)):
    rng = random.Random(seed)
    for _ in range(n):
        x0, y0, sp = rng.uniform(0, w + 40), rng.uniform(0, h), rng.uniform(*speed)
        y = (y0 + sp * t) % (h + 10) - 5
        x = (x0 - slant * sp * t) % (w + 40) - 20
        LN(d, [(x, y), (x - 1, y + 4)], c)


def snow(d, t, seed, n, w=VW, h=VH, c=(240, 244, 250), speed=(14, 30), wind=6.0):
    rng = random.Random(seed)
    for _ in range(n):
        x0, y0, sp, ph = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(*speed), rng.uniform(0, 6.28)
        y = (y0 + sp * t) % (h + 4) - 2
        x = (x0 + wind * t + 3 * math.sin(t * 1.3 + ph)) % w
        PX(d, x, y, c)
        if sp > 26:
            PX(d, x + 1, y, c)


# ---------------------------------------------------------------- the views
def v_street(d, t, weather):
    sky(d, (18, 22, 42), (34, 40, 66))
    R(d, 0, 46, VW - 1, 125, (44, 38, 52))
    for x in range(0, VW, 6):
        R(d, x, 48, x, 125, (38, 33, 46))
    for (x0, y0, x1, y1) in [(140, 56, 156, 72), (164, 52, 180, 70), (110, 86, 132, 108), (220, 60, 240, 78)]:
        R(d, x0, y0, x1, y1, (226, 168, 92))
        for x in range(x0 + 4, x1, 4):
            R(d, x, y0, x, y1, (176, 120, 66))
        R(d, x0, (y0 + y1) // 2, x1, (y0 + y1) // 2, (176, 120, 66))
    for r, a in [(9, 0.25), (6, 0.45)]:
        E(d, 146 - r, 108 - r, 146 + r, 116 + r, (int(90 + 120 * a), int(40 + 30 * a), 50))
    chochin(d, 146, 106)
    R(d, 188, 0, 191, 125, (24, 22, 30))
    LN(d, [(0, 18), (190, 10), (VW, 14)], (20, 18, 26))
    LN(d, [(0, 26), (190, 14), (VW, 20)], (20, 18, 26))
    R(d, 250, 92, 262, 125, (60, 70, 90))                 # vending machine
    R(d, 252, 95, 260, 104, (200, 230, 250))
    for i, x in enumerate(range(252, 261, 3)):
        R(d, x, 107, x + 1, 112, ((220, 80, 80), (80, 160, 220), (240, 200, 80))[i % 3])
    R(d, 0, 125, VW - 1, VH - 1, (30, 30, 42) if weather != 'snow' else (196, 200, 214))
    if weather != 'snow':
        for x0, c in [(146, (150, 60, 50)), (120, (150, 110, 70)), (256, (120, 160, 200))]:
            for y in range(130, VH, 3):
                R(d, x0 - 1 + (y // 3) % 2, y, x0 + 1 + (y // 3) % 2, y, c)


def v_edo_road(d, t, weather):
    sky(d, (34, 48, 66), (74, 92, 100))
    ridge(d, [(0, 70), (40, 50), (80, 62), (120, 44), (170, 60), (220, 48), (270, 58), (VW, 52)], (58, 76, 92))
    ridge(d, [(0, 86), (50, 72), (100, 82), (150, 68), (210, 80), (260, 70), (VW, 78)], (44, 60, 72))
    for y in (80, 92):
        R(d, 0, y, VW - 1, y + 3, (80, 96, 104))
    R(d, 0, 104, VW - 1, VH - 1, (40, 56, 50))
    PG(d, [(110, VH), (152, 104), (168, 104), (210, VH)], (96, 88, 74))
    for (x, y) in [(150, 160), (162, 136), (156, 120), (172, 150), (160, 110)]:
        E(d, x, y, x + 4, y + 2, (120, 112, 96))
    stone_lantern(d, 186, 106)
    pine(d, 128, 112, 1.0)
    pine(d, 250, 118, 1.3)
    R(d, 60, 96, 63, 120, (60, 44, 36))                 # milestone post
    R(d, 59, 95, 64, 96, (60, 44, 36))


def v_river(d, t, weather):
    sky(d, (20, 30, 52), (44, 62, 84))
    moon(d, 230, 34, 8)
    ridge(d, [(0, 80), (60, 70), (130, 78), (200, 66), (260, 76), (VW, 70)], (34, 48, 60))
    R(d, 0, 92, VW - 1, VH - 1, (30, 46, 66))
    for y in range(96, VH, 4):
        for x in range(((y * 7) % 11), VW, 14):
            R(d, x + int(3 * math.sin(t * 1.4 + y)), y, x + 5 + int(3 * math.sin(t * 1.4 + y)), y, (52, 72, 96))
    for i in range(5):
        y = 104 + i * 12
        R(d, 226 + int(2 * math.sin(t * 2 + i)), y, 234 + int(2 * math.sin(t * 2 + i)), y, (210, 210, 170))
    for x in list(range(0, 60, 5)) + list(range(270, VW, 5)):
        h = 18 + (x * 7) % 13
        LN(d, [(x, VH), (x + 2, VH - h)], (40, 70, 50))
        PX(d, x + 2, VH - h - 1, (110, 90, 60))
    R(d, 130, 86, 190, 92, (70, 56, 44))                 # far bank / bridge
    for x in range(134, 190, 10):
        R(d, x, 92, x + 1, 100, (60, 46, 36))


def v_sea(d, t, weather, island=True, dawn=False):
    if dawn:
        sky(d, (70, 80, 120), (240, 170, 120), 0, 100)
    else:
        sky(d, (20, 28, 52), (50, 60, 90), 0, 100)
        moon(d, 80, 30, 7)
    if island:
        ridge(d, [(150, 96), (170, 84), (196, 82), (214, 92)], (30, 40, 50), 100)
        pine(d, 182, 86, 0.35, c=(20, 30, 36), hi=(28, 40, 44))
    R(d, 0, 98, VW - 1, VH - 1, (34, 56, 84) if not dawn else (80, 100, 140))
    for y in range(100, VH, 3):
        for x in range(((y * 5) % 17), VW, 18):
            xx = x + int(4 * math.sin(t * 1.1 + y * 0.3))
            R(d, xx, y, xx + 6, y, (70, 96, 130) if not dawn else (220, 170, 150))
    bx = 120 + 6 * math.sin(t * 0.5)
    by = 124 + 2 * math.sin(t * 1.3)
    PG(d, [(bx - 16, by), (bx + 16, by), (bx + 12, by + 5), (bx - 12, by + 5)], (90, 64, 44))
    R(d, 0, 150, VW - 1, VH - 1, (150, 140, 110) if not island else (34, 56, 84))


def v_coast_dawn(d, t, weather):
    v_sea(d, t, weather, island=False, dawn=True)
    ridge(d, [(0, 110), (70, 100), (140, 120), (200, 140), (VW, 150)], (60, 70, 60))
    R(d, 0, 158, VW - 1, VH - 1, (176, 160, 120))
    for x in range(20, VW, 30):
        R(d, x, 150, x + 1, 158, (90, 70, 50))           # survey poles
        R(d, x - 2, 150, x + 3, 151, (220, 60, 50))


def v_forest(d, t, weather):
    sky(d, (16, 24, 30), (30, 44, 44))
    rng = random.Random(4)
    for layer, (c, n) in enumerate([((30, 44, 42), 14), ((22, 34, 32), 10), ((16, 24, 24), 7)]):
        for _ in range(n):
            x = rng.randrange(-10, VW)
            w = 6 + layer * 4
            R(d, x, 0, x + w, VH, c)
    for y, a in ((100, 0.3), (120, 0.5)):
        R(d, 0, y, VW - 1, y + 6, (60, 76, 74))
    R(d, 0, 140, VW - 1, VH - 1, (34, 44, 34))
    stone_lantern(d, 160, 150)
    for i in range(8):
        x = (i * 41 + t * 6) % VW
        y = 110 + 20 * math.sin(t * 0.7 + i)
        PX(d, x, y, (200, 230, 140))


def v_edo_town(d, t, weather, castle=False):
    sky(d, (22, 26, 44), (44, 46, 66))
    if castle:
        ridge(d, [(60, 90), (90, 70), (230, 70), (260, 90)], (54, 58, 70), 100)
        for (x0, x1, y) in ((120, 200, 54), (132, 188, 40), (144, 176, 28)):
            PG(d, [(x0 - 8, y + 8), (x1 + 8, y + 8), (x1, y), (x0, y)], (40, 44, 56))
            R(d, x0, y + 8, x1, y + 14, (210, 210, 214))
        PG(d, [(150, 20), (170, 20), (164, 14), (156, 14)], (40, 44, 56))
    wood_house(d, 0, 90, 150, 50, seed=1)
    wood_house(d, 230, 320, 150, 56, seed=2)
    wood_house(d, 92, 150, 140, 40, seed=3, lit=not castle)
    for x in (50, 110, 270):
        chochin(d, x, 104)
    R(d, 0, 150, VW - 1, VH - 1, (60, 52, 50) if weather != 'snow' else (200, 204, 216))
    if weather != 'snow':
        for y in range(154, VH, 3):
            R(d, 108 + (y // 3) % 2, y, 112 + (y // 3) % 2, y, (150, 70, 50))
    if castle:
        R(d, 120, 128, 200, 150, (70, 64, 60))           # the gate
        R(d, 140, 134, 180, 150, (40, 32, 30))
        PG(d, [(116, 128), (204, 128), (196, 120), (124, 120)], (40, 44, 56))


def v_bamboo(d, t, weather):
    sky(d, (16, 22, 44), (40, 52, 80))
    moon(d, 160, 46, 18, c=(252, 246, 214), glow=(70, 80, 120))
    rng = random.Random(9)
    for layer, (c, hi, n) in enumerate([((40, 70, 58), (60, 96, 74), 12), ((30, 58, 46), (52, 88, 64), 9),
                                         ((22, 44, 36), (40, 70, 50), 6)]):
        for _ in range(n):
            x = rng.randrange(-10, VW)
            if 130 < x < 190 and layer < 2:
                continue
            w = 3 + layer * 2
            R(d, x, 0, x + w, VH, c)
            R(d, x + 1, 0, x + 1, VH, hi)
            for y in range(rng.randrange(10, 30), VH, rng.randrange(22, 34)):
                R(d, x, y, x + w, y, shade(c, 0.7))
    R(d, 0, 160, VW - 1, VH - 1, (30, 40, 34))
    gx = 162
    for r, k in ((10, 0.25), (6, 0.5)):
        E(d, gx - r, 120 - r, gx + r, 120 + r, mix((40, 70, 58), (250, 240, 180), k))
    R(d, gx - 2, 104, gx + 2, 140, (210, 220, 150))          # the glowing stalk


def v_storm(d, t, weather):
    sky(d, (14, 14, 24), (40, 40, 56))
    rng = random.Random(5)
    for i in range(14):
        x, y, w = rng.randrange(-40, VW), rng.randrange(0, 90), rng.randrange(40, 110)
        E(d, x, y, x + w, y + 30, (36, 36, 50) if i % 2 else (50, 48, 66))
    R(d, 0, 140, VW - 1, VH - 1, (24, 26, 34))
    ph = (t * 0.7) % 3.0
    if ph < 0.15:
        x = 150
        pts = [(x, 0)]
        rr = random.Random(int(t * 0.7))
        for y in range(10, 150, 12):
            x += rr.randint(-10, 10)
            pts.append((x, y))
        LN(d, pts, (250, 250, 220), 2)


def v_heian(d, t, weather):
    sky(d, (18, 22, 46), (40, 44, 74))
    moon(d, 250, 34, 9)
    R(d, 0, 100, VW - 1, 140, (30, 52, 70))                 # pond
    for y in range(102, 140, 4):
        for x in range(((y * 3) % 13), VW, 16):
            R(d, x, y, x + 5, y, (44, 70, 92))
    for i in range(5):
        R(d, 244 + int(2 * math.sin(t + i)), 106 + i * 6, 256 + int(2 * math.sin(t + i)), 106 + i * 6, (210, 210, 170))
    pine(d, 60, 104, 0.9)
    R(d, 0, 140, VW - 1, VH - 1, (90, 60, 50))              # veranda boards
    for x in range(0, VW, 10):
        R(d, x, 140, x, VH, (70, 46, 38))
    R(d, 0, 132, VW - 1, 134, (196, 62, 48))                # vermilion rail
    for x in range(20, VW, 50):
        R(d, x, 120, x + 3, 140, (196, 62, 48))
        R(d, x - 1, 119, x + 4, 120, (226, 190, 80))


def v_meiji(d, t, weather):
    sky(d, (22, 24, 40), (46, 44, 62))
    for (x0, x1, h, c) in ((0, 110, 80, (140, 66, 52)), (210, 320, 90, (150, 72, 56))):
        R(d, x0, 150 - h, x1, 150, c)
        for y in range(150 - h, 150, 4):
            R(d, x0, y, x1, y, shade(c, 0.85))
        for x in range(x0 + 8, x1 - 10, 20):
            for y in range(150 - h + 10, 140, 26):
                R(d, x, y, x + 9, y + 14, (226, 180, 100))
                R(d, x, y, x + 9, y + 1, (230, 226, 216))
    R(d, 0, 150, VW - 1, VH - 1, (70, 66, 64) if weather != 'snow' else (200, 204, 216))
    for x in (124, 196):                                     # gas lamps
        R(d, x, 104, x + 1, 150, (40, 40, 44))
        R(d, x - 3, 98, x + 4, 104, (40, 40, 44))
        R(d, x - 2, 99, x + 3, 103, (255, 220, 140))
        for r, a in ((12, 0.12), (7, 0.25)):
            E(d, x - r, 101 - r, x + r, 101 + r, mix((46, 44, 62), (255, 220, 140), a))
    cx = 156                                                  # rickshaw
    E(d, cx - 8, 142, cx + 8, 158, (40, 34, 30))
    E(d, cx - 6, 144, cx + 6, 156, (70, 66, 64))
    R(d, cx - 10, 136, cx + 6, 142, (40, 34, 30))
    LN(d, [(cx + 6, 140), (cx + 30, 146)], (90, 70, 50))


def v_shibuya(d, t, weather):
    sky(d, (60, 60, 80), (110, 100, 110))
    R(d, 60, 70, 260, 140, (178, 170, 150))                 # station building
    R(d, 60, 64, 260, 70, (120, 110, 100))
    for x in range(72, 250, 18):
        R(d, x, 84, x + 10, 104, (90, 100, 110))
        R(d, x, 84, x + 10, 85, (220, 216, 200))
    E(d, 150, 72, 170, 92, (240, 236, 220))                 # clock
    LN(d, [(160, 82), (160, 76)], (40, 40, 40))
    LN(d, [(160, 82), (165, 82)], (40, 40, 40))
    R(d, 140, 112, 180, 140, (60, 56, 60))                  # entrance
    R(d, 0, 140, VW - 1, VH - 1, (96, 92, 92))
    for y in (150, 162):
        R(d, 0, y, VW - 1, y, (70, 70, 74))
    for x in (40, 280):
        R(d, x, 90, x + 1, 140, (40, 40, 44))
        R(d, x - 2, 88, x + 3, 90, (40, 40, 44))


def v_snow_mtn(d, t, weather):
    sky(d, (40, 48, 70), (120, 130, 150))
    ridge(d, [(0, 70), (60, 40), (120, 60), (180, 30), (250, 56), (VW, 40)], (200, 206, 220))
    ridge(d, [(0, 100), (80, 80), (160, 96), (240, 78), (VW, 92)], (226, 230, 240))
    R(d, 0, 120, VW - 1, VH - 1, (236, 240, 248))
    for x in (40, 90, 230, 280):
        PG(d, [(x, 120), (x + 10, 84), (x + 20, 120)], (30, 50, 44))
        PG(d, [(x + 4, 104), (x + 10, 88), (x + 16, 104)], (236, 240, 248))


def v_plum_snow(d, t, weather):
    sky(d, (40, 44, 70), (90, 96, 120))
    R(d, 0, 136, VW - 1, VH - 1, (230, 234, 244))
    R(d, 220, 70, 300, 136, (160, 50, 44))                  # shrine building
    PG(d, [(210, 72), (310, 72), (290, 56), (230, 56)], (60, 56, 64))
    PG(d, [(210, 72), (310, 72), (296, 64), (224, 64)], (236, 240, 248))
    tx = 120                                                 # the plum tree
    LN(d, [(tx, 136), (tx - 4, 110), (tx - 20, 90), (tx - 30, 84)], (70, 46, 38), 3)
    LN(d, [(tx - 4, 110), (tx + 14, 88), (tx + 30, 80)], (70, 46, 38), 2)
    LN(d, [(tx - 10, 100), (tx - 4, 80)], (70, 46, 38), 2)
    rng = random.Random(3)
    for _ in range(60):
        x = tx + rng.randint(-34, 34)
        y = rng.randint(72, 112)
        PX(d, x, y, (250, 170, 196) if rng.random() < 0.7 else (255, 240, 244))


def v_dream(d, t, weather):
    sky(d, (40, 26, 70), (110, 70, 130))
    stars(d, 11, 90, 120, (250, 240, 200))
    for i in range(6):
        x = (i * 70 + t * 8) % (VW + 80) - 40
        y = 40 + i * 20
        for dx, r in ((0, 12), (14, 16), (30, 11)):
            E(d, x + dx - r, y - r * 0.6, x + dx + r, y + r * 0.6, (190, 150, 210))
    moon(d, 250, 40, 10, c=(252, 236, 180), glow=(90, 60, 130))


def v_shrine_snow(d, t, weather):
    sky(d, (34, 36, 60), (80, 84, 110))
    R(d, 0, 140, VW - 1, VH - 1, (232, 236, 246))
    for (x0, s) in ((96, 1.0), (60, 0.6)):
        w = int(70 * s)
        h = int(90 * s)
        R(d, x0, 140 - h, x0 + 5, 140, (200, 56, 44))
        R(d, x0 + w, 140 - h, x0 + w + 5, 140, (200, 56, 44))
        R(d, x0 - 8, 140 - h - 8, x0 + w + 13, 140 - h - 4, (200, 56, 44))
        R(d, x0 - 10, 140 - h - 11, x0 + w + 15, 140 - h - 8, (40, 36, 40))
        R(d, x0 - 10, 140 - h - 12, x0 + w + 15, 140 - h - 12, (236, 240, 248))
        R(d, x0 - 2, 140 - h + 8, x0 + w + 7, 140 - h + 11, (200, 56, 44))
    for x in (40, 236):                                      # fox statues
        R(d, x - 6, 124, x + 6, 140, (150, 150, 146))
        E(d, x - 5, 104, x + 5, 126, (176, 176, 170))
        PG(d, [(x - 4, 106), (x - 3, 98), (x - 1, 105)], (176, 176, 170))
        PG(d, [(x + 4, 106), (x + 3, 98), (x + 1, 105)], (176, 176, 170))
        R(d, x - 4, 116, x + 4, 118, (200, 56, 44))
        R(d, x - 7, 103, x + 7, 104, (236, 240, 248))
    for x in range(20, VW, 40):
        stone_lantern(d, x + 150 if x < 170 else x, 140)


def v_kyoto_river(d, t, weather):
    sky(d, (22, 26, 50), (60, 54, 80))
    ridge(d, [(0, 70), (80, 56), (160, 66), (240, 52), (VW, 64)], (36, 46, 60))
    R(d, 0, 100, VW - 1, 130, (36, 56, 76))
    for y in range(102, 130, 4):
        for x in range(((y * 5) % 11), VW, 15):
            R(d, x, y, x + 5, y, (54, 76, 100))
    R(d, 0, 130, VW - 1, VH - 1, (150, 138, 116))           # the dry riverbed
    R(d, 100, 120, 220, 132, (120, 86, 56))                  # a plank stage
    R(d, 100, 118, 220, 120, (160, 120, 80))
    for x in (106, 214):
        R(d, x, 80, x + 2, 120, (100, 70, 46))
    LN(d, [(106, 82), (160, 90), (216, 82)], (60, 50, 40))
    for i, x in enumerate(range(116, 210, 14)):
        chochin(d, x, 86 + int(3 * math.sin(i)), (230, 180, 80) if i % 2 else (214, 70, 50))


VIEWS = {
    'street': (v_street, (146, 60)),
    'edo_road': (v_edo_road, (160, 60)),
    'river': (v_river, (226, 60)),
    'sea': (v_sea, (182, 60)),
    'coast': (v_coast_dawn, (60, 80)),
    'forest': (v_forest, (160, 76)),
    'edo_town': (v_edo_town, (110, 76)),
    'edo_castle': (lambda d, t, w: v_edo_town(d, t, w, castle=True), (160, 72)),
    'bamboo': (v_bamboo, (162, 60)),
    'storm': (v_storm, (150, 50)),
    'heian': (v_heian, (250, 60)),
    'meiji': (v_meiji, (124, 70)),
    'shibuya': (v_shibuya, (160, 62)),
    'snow_mtn': (v_snow_mtn, (180, 70)),
    'plum': (v_plum_snow, (120, 64)),
    'dream': (v_dream, (160, 50)),
    'shrine': (v_shrine_snow, (130, 62)),
    'kyoto_river': (v_kyoto_river, (160, 62)),
}

# weather a view has on its own (the door shows the visitor's world, not ours)
VIEW_WEATHER = {
    'edo_road': 'rain', 'river': 'rain', 'sea': 'clear', 'coast': 'clear', 'forest': 'rain', 'edo_town': 'rain',
    'edo_castle': 'snow', 'bamboo': 'clear', 'storm': 'storm', 'heian': 'clear', 'meiji': 'rain', 'shibuya': 'rain',
    'snow_mtn': 'blizzard', 'plum': 'snow', 'dream': 'clear', 'shrine': 'snow', 'kyoto_river': 'clear',
}

_cache = {}


def view(name, t, weather='rain'):
    """The whole 320x180 view at time t (weather particles move; the rest is cached)."""
    fn, _ = VIEWS[name]
    w = weather if name == 'street' else VIEW_WEATHER.get(name, 'clear')
    key = (name, w)
    if key not in _cache:
        im = Image.new('RGB', (VW, VH))
        fn(ImageDraw.Draw(im), 0.0 if name not in ('storm', 'river', 'sea', 'coast', 'heian', 'kyoto_river') else 0.0, w)
        _cache[key] = im
    animated = name in ('river', 'sea', 'coast', 'storm', 'heian', 'forest', 'dream')
    if animated:
        im = Image.new('RGB', (VW, VH))
        fn(ImageDraw.Draw(im), t, w)
    else:
        im = _cache[key].copy()
    d = ImageDraw.Draw(im)
    if w in ('rain', 'storm'):
        rain(d, t, 7, (150, 170, 210), 160 if w == 'rain' else 260)
    elif w == 'snow':
        snow(d, t, 8, 220)
    elif w == 'blizzard':
        snow(d, t, 8, 420, speed=(30, 60), wind=60.0)
    return im


def door_crop(name, t, weather='rain'):
    """The 41x80 piece of a view seen through the open door."""
    fx, fy = VIEWS[name][1]
    x0 = max(0, min(VW - 41, fx - 20))
    y0 = max(0, min(VH - 80, fy))
    return view(name, t, weather).crop((x0, y0, x0 + 41, y0 + 80))
