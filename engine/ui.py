"""Text and cards drawn over the scene.

Landscape: a 640x360 RGBA layer (scene pixels x2).  Shorts: a 360x640 layer whose middle
(y 110-470) shows a 180x180 crop of the scene at x2.  Everything uses GNU Unifont at its
native 16px and is scaled x3 by ffmpeg, so letters stay crisp.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from .gfx import FONT, C, text_w, wrap, text_img, glyph_mask

INK = (46, 36, 40)
CREAM = (244, 236, 220)
GOLD = (236, 196, 110)
SPEAKER_COL = dict(haru=(255, 180, 120), kon=(255, 160, 80), mika=(150, 200, 255), gen=(200, 200, 170),
                   cho=(255, 220, 140))


def panel(d, x0, y0, x1, y1, fill, border, inner):
    d.rectangle([x0, y0, x1, y1], fill=border)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=inner)
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=fill)


def _alpha(im, a):
    if a >= 0.999:
        return im
    arr = np.asarray(im).copy()
    arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def brush_glyph(ch, scale, color):
    """A character drawn big, as if with a brush: the glyph at x`scale` with soft ragged edges."""
    m = glyph_mask(ch)
    h, w = m.shape
    big = np.kron(m, np.ones((scale, scale), bool))
    # thicken a little and nibble the edges for a hand-made look
    th = big.copy()
    th[1:] |= big[:-1]
    th[:, 1:] |= big[:, :-1]
    yy, xx = np.mgrid[0:th.shape[0], 0:th.shape[1]]
    nib = ((xx * 7 + yy * 13) % 11 == 0) & ~big
    th &= ~nib
    out = np.zeros((th.shape[0], th.shape[1], 4), np.uint8)
    out[th] = (*color, 255)
    return Image.fromarray(out, 'RGBA')


class Overlay:
    def __init__(self, fmt, cast, words, facts, meta=None):
        self.fmt = fmt
        self.cast = cast
        self.words = words
        self.facts = facts
        self.meta = meta or {}
        self.size = (640, 360) if fmt == 'landscape' else (360, 640)
        self._cache = {}

    # ------------------------------------------------------------ pieces
    def _dialogue(self, d, st):
        ln = st.get('line')
        if not ln:
            return
        who = ln['who']
        name = self.cast[who]['name'] if who in self.cast else who
        ncol = SPEAKER_COL.get(who, (226, 200, 140))
        if self.fmt == 'landscape':
            bx0, by0, bx1, by1, tx, ty, maxw, nlines = 24, 286, 616, 352, 40, 302, 568, 2
        else:
            bx0, by0, bx1, by1, tx, ty, maxw, nlines = 8, 424, 326, 502, 18, 438, 300, 3
        panel(d, bx0, by0, bx1, by1, (30, 22, 30, 236), (238, 224, 194, 255), (96, 72, 62, 255))
        nw = text_w(name) + 16
        panel(d, bx0 + 12, by0 - 12, bx0 + 12 + nw, by0 + 8, (30, 22, 30, 255), (238, 224, 194, 255), (96, 72, 62, 255))
        d.text((bx0 + 20, by0 - 10), name, font=FONT, fill=ncol)
        lines = wrap(ln['text'], maxw)
        left = ln['shown']
        y = ty
        for l in lines[:nlines]:
            d.text((tx, y), l[:max(0, left)], font=FONT, fill=CREAM)
            left -= len(l) + 1
            y += 19

    def _fact(self, canvas, card):
        f = self.facts[card['id']]
        if self.fmt == 'landscape':
            x0, x1, maxw, yb = 20, 620, 524, 4
        else:
            x0, x1, maxw, yb = 6, 354, 296, 54
        key = ('fact', card['id'], self.fmt)
        if key not in self._cache:
            body = wrap(f['body'], maxw)
            title = wrap(f['title'], maxw)
            h = 12 + len(title) * 18 + 6 + len(body) * 18 + 8
            im = Image.new('RGBA', (x1 - x0 + 1, h + 1), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.fontmode = '1'
            panel(d, 0, 0, x1 - x0, h, (244, 234, 208, 250), (110, 76, 52, 255), (200, 176, 140, 255))
            y = 8
            for tl in title:
                d.text((14, y), tl, font=FONT, fill=(166, 50, 38))
                y += 18
            d.line([(14, y + 1), (x1 - x0 - 44, y + 1)], fill=(200, 176, 140), width=1)
            y += 6
            for l in body:
                d.text((14, y), l, font=FONT, fill=INK)
                y += 18
            sx0 = x1 - x0 - 36
            d.rectangle([sx0, 8, sx0 + 26, 8 + 56], fill=(192, 52, 44))
            d.rectangle([sx0 + 2, 10, sx0 + 24, 62], outline=(244, 220, 200))
            for k, ch in enumerate('豆知識'):
                d.text((sx0 + 5, 11 + k * 16), ch, font=FONT, fill=(250, 236, 224))
            self._cache[key] = im
        im = self._cache[key]
        u = card['u']
        y = int(yb - (im.height + 8) * (1 - u))
        canvas.alpha_composite(im, (x0, max(-im.height, y)))

    def _word(self, canvas, card):
        w = self.words[card['id']]
        jp, ro, mean = w['jp'], w['romaji'], w['meaning']
        key = ('word', card['id'], self.fmt)
        maxw = 232 if self.fmt == 'landscape' else 316
        if key not in self._cache:
            ml = wrap(mean, maxw)
            h = 10 + 18 + 18 + len(ml) * 18 + 6
            width = maxw + 24
            im = Image.new('RGBA', (width + 1, h + 1), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.fontmode = '1'
            panel(d, 0, 0, width, h, (36, 44, 84, 240), (226, 210, 170, 255), (80, 90, 140, 255))
            d.text((12, 7), jp, font=FONT, fill=(250, 240, 220))
            d.text((12, 25), ro, font=FONT, fill=(255, 186, 120))
            y = 43
            for l in ml:
                d.text((12, y), l, font=FONT, fill=(206, 214, 236))
                y += 18
            self._cache[key] = im
        im = self._cache[key]
        im = _alpha(im, card['u'])
        if self.fmt == 'landscape':
            canvas.alpha_composite(im, (640 - im.width - 8, 6))
        else:
            canvas.alpha_composite(im, ((360 - im.width) // 2, 56))

    def _name(self, canvas, card, y_override=None):
        c = self.cast[card['id']]
        key = ('name', card['id'], self.fmt)
        if key not in self._cache:
            l1 = f"{c['name_jp']}  {c['name']}"
            l2 = f"{c['role']} · {c['era']}"
            width = max(text_w(l1), text_w(l2)) + 24
            im = Image.new('RGBA', (width + 1, 50), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.fontmode = '1'
            panel(d, 0, 0, width, 46, (30, 22, 30, 236), (226, 200, 140, 255), (96, 72, 62, 255))
            d.text((12, 6), c['name_jp'], font=FONT, fill=GOLD)
            d.text((12 + text_w(c['name_jp']) + 16, 6), c['name'], font=FONT, fill=CREAM)
            d.text((12, 24), l2, font=FONT, fill=(190, 180, 170))
            self._cache[key] = im
        im = _alpha(self._cache[key], card['u'])
        if self.fmt == 'landscape':
            canvas.alpha_composite(im, (8, 6))
        else:
            canvas.alpha_composite(im, ((360 - im.width) // 2, y_override or 60))

    def board_image(self, who, scale=1):
        """The signed shikishi board for a visitor (used on screen and in thumbnails)."""
        key = ('board', who, scale)
        if key in self._cache:
            return self._cache[key]
        c = self.cast[who]
        W_, H_ = 120, 136
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.fontmode = '1'
        d.rectangle([0, 0, W_ - 1, H_ - 1], fill=(168, 124, 52))
        d.rectangle([2, 2, W_ - 3, H_ - 3], fill=(236, 196, 110))
        d.rectangle([5, 5, W_ - 6, H_ - 6], fill=(250, 246, 234))
        for yy in range(9, H_ - 9, 7):
            for xx in range(9 + (yy // 7 % 2) * 5, W_ - 9, 11):
                d.point((xx, yy), fill=(236, 224, 196))
        g = brush_glyph(c.get('emblem', '麺'), 4, (30, 24, 28))
        im.alpha_composite(g, (W_ // 2 - g.width // 2 + 8, 14))
        for k, ch in enumerate(c['name_jp'][:6]):
            d.text((12, 12 + k * 17), ch, font=FONT, fill=(40, 30, 34))
        d.rectangle([W_ - 28, H_ - 30, W_ - 11, H_ - 13], fill=(196, 52, 44))
        d.rectangle([W_ - 26, H_ - 28, W_ - 13, H_ - 15], outline=(250, 220, 210))
        sg = c['name_jp'][0]
        d.text((W_ - 27, H_ - 30), sg, font=FONT, fill=(250, 236, 224))
        if scale != 1:
            im = im.resize((W_ * scale, H_ * scale), Image.NEAREST)
        self._cache[key] = im
        return im

    def _sign(self, canvas, card):
        b = self.board_image(card['id'])
        u = card['u']
        cap = text_img('signed for the wall', (255, 220, 160), shadow=(30, 20, 26))
        if self.fmt == 'landscape':
            x, y = 320 - b.width // 2, int(10 - (b.height + 20) * (1 - u))
            canvas.alpha_composite(b, (x, max(-b.height, y)))
            canvas.alpha_composite(_alpha(cap, u), (320 - cap.width // 2, max(-20, y + b.height + 4)))
        else:
            x, y = 180 - b.width // 2, int(56 - (b.height + 20) * (1 - u))
            canvas.alpha_composite(b, (x, max(-b.height, y)))
            canvas.alpha_composite(_alpha(cap, u), (180 - cap.width // 2, max(-20, y + b.height + 4)))

    def _title(self, canvas, a, number, title):
        key = ('title', number, title, self.fmt)
        if key not in self._cache:
            lay = Image.new('RGBA', self.size, (0, 0, 0, 0))
            big = text_img('TIMESLIP RAMEN', (250, 236, 206), shadow=(40, 26, 30), scale=3)
            jp = text_img('タイムスリップ・ラーメン', (255, 186, 120), shadow=(40, 26, 30), scale=2)
            sub = self.meta.get('subtitle') or (f'Episode {number}' if number else '')
            ep = text_img(sub, (236, 224, 200), shadow=(40, 26, 30))
            tt = text_img(title, (255, 240, 210), shadow=(40, 26, 30), scale=2)
            W_ = self.size[0]
            band = Image.new('RGBA', (W_, 168), (20, 14, 22, 150))
            lay.alpha_composite(band, (0, 84))
            lay.alpha_composite(big, ((W_ - big.width) // 2, 92))
            lay.alpha_composite(jp, ((W_ - jp.width) // 2, 152))
            lay.alpha_composite(ep, ((W_ - ep.width) // 2, 200))
            lay.alpha_composite(tt, ((W_ - tt.width) // 2, 220))
            self._cache[key] = lay
        canvas.alpha_composite(_alpha(self._cache[key], a))

    def _end(self, canvas, a, text):
        key = ('end', text, self.fmt)
        if key not in self._cache:
            lay = Image.new('RGBA', self.size, (0, 0, 0, 0))
            W_ = self.size[0]
            head = self.meta.get('endhead', 'NEXT TIME AT TIMESLIP RAMEN')
            l1 = text_img(head, (255, 186, 120), shadow=(30, 20, 26), scale=2)
            lay.alpha_composite(l1, ((W_ - l1.width) // 2, 34))
            y = 80
            for part in text.split('|'):
                for l in wrap(part.strip(), 560):
                    im = text_img(l, (250, 236, 206), shadow=(30, 20, 26))
                    lay.alpha_composite(im, ((W_ - im.width) // 2, y))
                    y += 20
                y += 6
            l3 = text_img('New episodes Monday · Wednesday · Friday   ·   a new Short every day',
                          (210, 200, 186), shadow=(30, 20, 26))
            lay.alpha_composite(l3, ((W_ - l3.width) // 2, 330))
            self._cache[key] = lay
        canvas.alpha_composite(_alpha(self._cache[key], a))

    def _caption(self, canvas, text, a):
        im = text_img(text, (250, 240, 214), shadow=(20, 14, 20), scale=2 if self.fmt == 'landscape' else 1)
        if self.fmt == 'landscape':
            canvas.alpha_composite(_alpha(im, a), (24, 300))
        else:
            canvas.alpha_composite(_alpha(im, a), ((360 - im.width) // 2, 360))

    def _hook(self, canvas, text, a):
        lines = wrap(text, 160)
        band = Image.new('RGBA', (360, 20 + 36 * len(lines)), (20, 14, 22, 170))
        canvas.alpha_composite(_alpha(band, a), (0, 58))
        y = 68
        for l in lines:
            im = text_img(l, (255, 240, 200), shadow=(30, 20, 26), scale=2)
            canvas.alpha_composite(_alpha(im, a), ((360 - im.width) // 2, y))
            y += 36

    # ------------------------------------------------------------ frame
    def draw(self, st, t, hook=None, hook_a=0.0):
        canvas = Image.new('RGBA', self.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(canvas)
        d.fontmode = '1'
        est = st.get('establish')
        if est:
            if est.get('caption'):
                self._caption(canvas, est['caption'], min(1.0, est.get('a', 1.0)))
            return canvas
        self._dialogue(d, st)
        cards = st.get('cards', [])
        big = [c for c in cards if c['type'] in ('fact', 'sign')]
        if big:
            for c in big[-1:]:
                (self._fact if c['type'] == 'fact' else self._sign)(canvas, c)
        else:
            names = [c for c in cards if c['type'] == 'name']
            words = [c for c in cards if c['type'] == 'word']
            if self.fmt == 'landscape':
                for c in names[-1:]:
                    self._name(canvas, c)
                for c in words[-1:]:
                    self._word(canvas, c)
            else:
                if hook and hook_a > 0:
                    self._hook(canvas, hook, hook_a)
                elif words:
                    self._word(canvas, words[-1])
                elif names:
                    self._name(canvas, names[-1])
        if st.get('title', 0) > 0 and self.fmt == 'landscape':
            self._title(canvas, st['title'], self.meta.get('number', 0), self.meta.get('title', ''))
        if st.get('end', 0) > 0 and self.fmt == 'landscape':
            self._end(canvas, st['end'], self.meta.get('end_text', ''))
        return canvas
