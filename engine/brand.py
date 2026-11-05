"""Channel art: the logo (a bowl whose naruto is a clock), the banner and the watermark.

The logo is drawn at 50x50 and blown up with nearest neighbour, so it stays a crisp pixel badge
even at YouTube's smallest avatar size.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .gfx import FONT, text_w
from .thumbs import big_words, INK, CREAM, GOLD

INDIGO = (30, 34, 66)
INDIGO2 = (44, 52, 96)
BOWL = (180, 44, 36)
BOWL_DK = (120, 26, 24)
RIM = (248, 238, 222)
BROTH = (226, 160, 72)
NOODLE = (252, 226, 150)
PINK = (232, 92, 128)
STEAM = (220, 226, 240)


def logo_1x(n=50):
    im = Image.new('RGB', (n, n), INDIGO)
    d = ImageDraw.Draw(im)
    # a soft ring of wave scales behind, like the noren pattern
    for r, col in ((24, INDIGO2), (21, INDIGO), (18, (38, 44, 82))):
        d.ellipse((25 - r, 25 - r, 24 + r, 24 + r), outline=col)
    # steam: two curls that read as a little time spiral
    for (x0, ph) in ((19, 0.0), (29, 1.7)):
        for i in range(10):
            y = 17 - i
            x = x0 + round(2.2 * math.sin(i * 0.75 + ph))
            d.point((x, y), fill=STEAM if i < 8 else (160, 170, 200))
    # bowl
    d.pieslice((7, 14, 42, 46), 0, 180, fill=BOWL)
    d.rectangle((7, 29, 42, 30), fill=RIM)                    # rim
    d.line((10, 37, 39, 37), fill=BOWL_DK)                     # band
    for x in range(12, 38, 4):                                  # raimon zigzag on the band
        d.point((x, 36), fill=RIM)
        d.point((x + 1, 38), fill=RIM)
    d.rectangle((19, 45, 30, 46), fill=BOWL_DK)                # foot
    # broth and noodles peeking above the rim
    d.rectangle((9, 27, 40, 28), fill=BROTH)
    for x in (11, 14, 17, 33, 36, 39):
        d.point((x, 26), fill=NOODLE)
        d.point((x, 27), fill=NOODLE)
    # chopsticks
    d.line((31, 27, 43, 9), fill=(196, 150, 96))
    d.line((33, 27, 45, 11), fill=(166, 120, 70))
    # the naruto: a clock face with a pink spiral and two hands
    cx, cy, r = 22, 23, 8
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RIM, outline=(200, 190, 180))
    seen = set()
    a = 0.0
    while a < 4.1 * math.pi:                                    # two turns of pink spiral
        rr = 1.2 + a * (4.6 / (4 * math.pi))
        p = (round(cx + rr * math.cos(a + 1.0)), round(cy + rr * math.sin(a + 1.0)))
        if p not in seen:
            seen.add(p)
            d.point(p, fill=PINK)
        a += 0.04
    for i in range(4):                                          # 12, 3, 6 and 9 o'clock
        a = i * math.pi / 2
        d.point((round(cx + r * math.cos(a)), round(cy + r * math.sin(a))), fill=PINK)
    d.line((cx, cy, cx, cy - 4), fill=INK)                      # hands at ten past
    d.line((cx, cy, cx + 3, cy - 1), fill=INK)
    d.point((cx, cy), fill=INK)
    return im


def logo(size=800):
    im = logo_1x()
    return im.resize((size, size), Image.NEAREST)


def watermark(size=150):
    im = logo_1x().resize((150, 150), Image.NEAREST).convert('RGBA')
    m = Image.new('L', (150, 150), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255)
    im.putalpha(m)
    return im.resize((size, size), Image.NEAREST)


def words(s, color, scale, bold=True, outline=True):
    """One line of Unifont at an integer scale with an ink outline (no shadow)."""
    tw = text_w(s) + (1 if bold else 0)
    m = Image.new('L', (tw + 6, 21), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((3, 2), s, font=FONT, fill=255)
    if bold:
        d.text((4, 2), s, font=FONT, fill=255)
    lay = Image.new('RGBA', m.size, (0, 0, 0, 0))
    if outline:
        lay.paste(Image.new('RGBA', m.size, INK + (255,)), (0, 0), m.filter(ImageFilter.MaxFilter(3)))
    lay.paste(Image.new('RGBA', m.size, color + (255,)), (0, 0), m)
    bb = lay.getbbox()
    lay = lay.crop(bb)
    return lay.resize((lay.width * scale, lay.height * scale), Image.NEAREST)


def banner(scene, W=2560, H=1440):
    """scene: a 320x180 frame of the shop.  Shown whole on TVs; desktops see the middle strip
    (2560x423) and phones the safe area (1546x423), where the logo, name and schedule sit."""
    bg = scene.resize((W, H), Image.NEAREST).convert('RGBA')
    sx0, sx1 = (W - 1546) // 2, (W + 1546) // 2
    sy0, sy1 = (H - 423) // 2, (H + 423) // 2
    # darken the desktop strip a little so the panel sits in a pool of shade
    shade = Image.new('RGBA', (W, sy1 - sy0 + 80), (16, 12, 24, 90))
    bg.alpha_composite(shade, (0, sy0 - 40))
    # the panel: the safe area, in the colours of the episode title band
    panel = Image.new('RGBA', (sx1 - sx0, sy1 - sy0), (20, 18, 34, 226))
    pd = ImageDraw.Draw(panel)
    pd.rectangle((0, 0, panel.width - 1, panel.height - 1), outline=GOLD + (255,), width=8)
    pd.rectangle((12, 12, panel.width - 13, panel.height - 13), outline=(110, 80, 50, 255), width=4)
    bg.alpha_composite(panel, (sx0, sy0))
    lg = logo_1x().resize((350, 350), Image.NEAREST)
    m = Image.new('L', (350, 350), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 349, 349), fill=255)
    lg = lg.convert('RGBA')
    lg.putalpha(m)
    bg.alpha_composite(lg, (sx0 + 44, sy0 + (sy1 - sy0 - 350) // 2))
    tx = sx0 + 44 + 350 + 56
    t1 = words('TIMESLIP RAMEN', CREAM, 9)
    t2 = words('タイムスリップ・ラーメン', GOLD, 4, bold=False)
    t3 = words('MON · WED · FRI  +  A SHORT EVERY DAY', (200, 206, 232), 3, bold=False)
    total = t1.height + 26 + t2.height + 30 + t3.height
    y = sy0 + (sy1 - sy0 - total) // 2
    for t, gap in ((t1, 26), (t2, 30), (t3, 0)):
        bg.alpha_composite(t, (tx, y))
        y += t.height + gap
    return bg.convert('RGB')
