"""Script -> timeline.

A script is plain text (content/scripts/epNN.txt):

    @title Two Hundred Years Too Early      header lines start with @
    @present gen:6                          regulars already seated when the episode opens
    > cook 6                                commands start with >; a trailing & runs it in parallel
    kon: Evening, Haru. [w:okaeri]          dialogue  who: text   (who>target: text sets the gaze)

The cursor moves forward through blocking commands and lines.  Each actor (Haru and every
customer) also has its own queue, so a parallel command never makes anyone teleport.
Timeline.state(t) returns everything the shop and the overlay need for one frame.
"""
import math
import random
import re
import shlex

from .gfx import SEATS, POT_X, DOOR_IN, FLOOR_Y, clamp, ease

TYPE_CPS = 38.0
GAP = 0.25


def read_time(text):
    return max(2.0, 1.0 + len(text) / 15.5)


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


class ScriptError(Exception):
    pass


class Timeline:
    def __init__(self, castmap, words=None, facts=None, boards0=(), name='ep'):
        self.cast = castmap
        self.words = words or {}
        self.facts = facts or {}
        self.name = name
        self.meta = dict(title='', weather='rain', music=['last_bowl'], number=0)
        self.segs = {}          # who -> [(t0, t1, fn(t) -> dict)]
        self.mods = {}          # who -> [(t0, t1, key, value)]
        self.haru = []          # [(t0, t1, fn)]
        self.haru_mods = []
        self.haru_end = (0.0, 205)
        self.haru_free = 0.0
        self.free = {}          # who -> time their queue is free
        self.seat = {}          # who -> x of their stool (current, while building)
        self.doors = []
        self.rattles = []
        self.bowls = []
        self.lines = []
        self.cards = []
        self.props = []
        self.boards0 = list(boards0)
        self.board_adds = []
        self.establish = []
        self.weather = [(0.0, 'rain')]
        self.flashes = []
        self.lights = []
        self.sfx = []
        self.labels = {}
        self.shorts = {}
        self.chapters = []
        self.cho = [(0.0, dict(eye='closed', look=(0, 0), tongue=False))]
        self.maneki = []
        self.staff = []          # (t0, t1, x, kind)
        self.hat_stool = []      # (t0, t1, x)
        self.end = None
        self.title_t = None
        self.duration = 0.0
        self.cur = 0.0
        self.teaser = None
        self.nameplates_done = set()
        self.cam_hint = []       # (t0, t1, x) where the action is (for Shorts)

    # ================================================================ building helpers
    def _seg(self, who, t0, t1, fn):
        self.segs.setdefault(who, []).append((t0, t1, fn))
        self.free[who] = max(self.free.get(who, 0.0), t1)

    def _mod(self, who, t0, t1, key, val):
        if who == 'haru':
            self.haru_mods.append((t0, t1, key, val))
        else:
            self.mods.setdefault(who, []).append((t0, t1, key, val))

    def _sfx(self, name, t, **kw):
        self.sfx.append((name, t, kw))

    def _haru_seg(self, t0, t1, fn, x_end):
        self.haru.append((t0, t1, fn))
        self.haru_free = max(self.haru_free, t1)
        if t1 >= self.haru_end[0]:
            self.haru_end = (t1, x_end)

    def haru_x_at(self, t):
        best = None
        for t0, t1, fn in self.haru:
            if t0 <= t < t1:
                if best is None or t0 >= best[0]:
                    best = (t0, fn)
        if best:
            return best[1](t)['x']
        x, te = 205, -1.0
        for t0, t1, fn in self.haru:
            if t1 <= t and t1 >= te:
                te, x = t1, fn(t1 - 1e-4)['x']
        return x

    def haru_walk(self, t0, x1, pose='walk', bowl=None, speed=62.0):
        x0 = self.haru_x_at(t0)
        if abs(x1 - x0) < 1:
            return t0
        dur = abs(x1 - x0) / speed

        def fn(t, t0=t0, dur=dur, x0=x0, x1=x1):
            u = clamp((t - t0) / dur, 0, 1)
            return dict(x=x0 + (x1 - x0) * u, pose=pose, bowl=bowl)
        self._haru_seg(t0, t0 + dur, fn, x1)
        return t0 + dur

    def haru_hold(self, t0, t1, x, pose='front', **kw):
        self._haru_seg(t0, t1, lambda t, x=x, pose=pose, kw=kw: dict(x=x, pose=pose, **kw), x)
        return t1

    def walk(self, who, pts, t0, speed=50.0, step='step', **extra):
        t = t0
        dist0 = 0.0
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            Ln = math.hypot(x1 - x0, y1 - y0)
            if Ln < 0.5:
                continue
            dur = Ln / speed
            f = 1 if x1 >= x0 else -1

            def fn(tt, t=t, dur=dur, x0=x0, y0=y0, x1=x1, y1=y1, Ln=Ln, dist0=dist0, f=f):
                u = clamp((tt - t) / dur, 0, 1)
                d = dict(who=who, mode='walk', x=x0 + (x1 - x0) * u, y=y0 + (y1 - y0) * u, f=f,
                         phase=(dist0 + Ln * u) / 9.0, pose='walk')
                d.update(extra)
                return d
            self._seg(who, t, t + dur, fn)
            nsteps = int((dist0 + Ln) / 9.0) - int(dist0 / 9.0)
            for k in range(nsteps):
                self._sfx(step, t + dur * (k + 1) / max(1, nsteps), who=who)
            t += dur
            dist0 += Ln
        return t

    def hold(self, who, t0, t1, **d):
        self._seg(who, t0, t1, lambda tt, d=d: dict(d, who=who))
        return t1

    def sit(self, who, x, t0, t1=1e9):
        def fn(tt, t0=t0, x=x):
            return dict(who=who, mode='sit', x=x, dy=-2 if 0 <= tt - t0 < 0.12 else 0)
        self._seg(who, t0, t1, fn)
        self.seat[who] = x
        return t0 + 0.2

    def door(self, t_open, t_close, outside, rattle=True):
        if rattle:
            self.rattles.append(t_open - 0.7)
            self._sfx('rattle', t_open - 0.7)
        self.doors.append(dict(t0=t_open, t1=t_close, outside=outside))
        self._sfx('door_open', t_open)
        self._sfx('chime', t_open + 0.25)
        self._sfx('door_close', t_close)
        if outside not in ('street',):
            self._sfx('shimmer', t_open + 0.1)

    def kind(self, who):
        return self.cast[who]['kind']

    # ================================================================ script execution
    def load(self, text):
        lines = text.split('\n')
        for ln_no, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            try:
                if line.startswith('@'):
                    self._header(line[1:])
                elif line.startswith('>'):
                    body = line[1:].strip()
                    par = body.endswith('&')
                    if par:
                        body = body[:-1].strip()
                    self._command(body, par)
                else:
                    self._dialogue(line)
            except ScriptError:
                raise
            except Exception as e:      # noqa
                raise ScriptError(f'{self.name} line {ln_no}: {raw!r}: {e!r}') from e
        self.duration = max(self.cur, self.end + 14.0 if self.end else self.cur + 2)
        return self

    def _header(self, s):
        key, _, val = s.partition(' ')
        val = val.strip()
        if key == 'title':
            self.meta['title'] = val
        elif key == 'number':
            self.meta['number'] = int(val)
        elif key == 'weather':
            self.weather = [(0.0, val)]
            self.meta['weather'] = val
        elif key == 'music':
            self.meta['music'] = val.split()
        elif key == 'present':
            for tok in val.split():
                who, _, seat = tok.partition(':')
                x = SEATS[int(seat) - 1]
                self.sit(who, x, -1.0)
                self.free[who] = 0.0
        elif key == 'teaser':
            lab, dur = val.split()
            self.teaser = (lab, float(dur))
        elif key == 'haru':
            x = float(val)
            self.haru_end = (0.0, x)
            self.haru_hold(-1.0, 0.0, x)
        elif key == 'cho':
            self.cho = [(0.0, self._cho_parse(val.split()))]
        elif key == 'kasa':
            # grandpa's old umbrella, asleep in the stand (it wakes up in Episode 3)
            self.hold('kasa', -1.0, 1e9, mode='stand', x=65, y=146, eye='closed', tongue=0)
            self.seat['kasa'] = 65
        elif key == 'zashiki':
            # the house spirit has lived in the corner since Episode 6
            self.hold('zashiki', -1.0, 1e9, mode='stand', x=86, y=147, f=1, phase=0.0)
            self.seat['zashiki'] = 86
        elif key == 'tails':
            self._mod('kon', -1.0, 1e9, 'tails', int(val))
        else:
            self.meta[key] = val

    def _kv(self, toks):
        pos, kw = [], {}
        for tk in toks:
            if '=' in tk:
                k, v = tk.split('=', 1)
                kw[k] = v
            else:
                pos.append(tk)
        return pos, kw

    def _where(self, spec):
        """'3' -> stool 3, 'floor:70', 'counter:200', 'x:120'."""
        spec = str(spec)
        if spec.isdigit():
            return ('seat', SEATS[int(spec) - 1])
        k, _, v = spec.partition(':')
        return (k, float(v))

    def _command(self, body, par):
        if body.startswith('end ') or body == 'end':
            self.cur = max(self.cur, self.c_end(self.cur, body[4:].strip()))
            return
        toks = shlex.split(body)
        cmd, args = toks[0], toks[1:]
        pos, kw = self._kv(args)
        c = self.cur
        fn = getattr(self, 'c_' + cmd, None)
        if fn is None:
            raise ScriptError(f'unknown command {cmd!r}')
        end = fn(c, *pos, **kw)
        if end is None:
            end = c
        if not par:
            self.cur = max(self.cur, end)

    # ------------------------------------------------------------- dialogue
    def _dialogue(self, line):
        m = re.match(r'^([a-z_]+)(?:>([a-z_]+))?\s*:\s*(.*)$', line)
        if not m:
            raise ScriptError(f'cannot parse {line!r}')
        who, to, text = m.group(1), m.group(2), m.group(3)
        if who not in self.cast:
            raise ScriptError(f'unknown speaker {who!r}')
        words = re.findall(r'\[w:([a-z0-9_]+)\]', text)
        cps = TYPE_CPS
        mm = re.search(r'\[slow\]', text)
        if mm:
            cps = 17.0
        extra = 0.0
        me = re.search(r'\[\+([\d.]+)\]', text)
        if me:
            extra = float(me.group(1))
        text = re.sub(r'\s*\[[^\]]*\]', '', text).strip()
        if to is None:
            prev = self.lines[-1] if self.lines else None
            if prev and prev['who'] != who and prev['t1'] > self.cur - 4:
                to = prev['who']
            else:
                to = 'haru' if who != 'haru' else None
        dur = read_time(text) * (TYPE_CPS / cps if cps < TYPE_CPS else 1.0) + extra
        t0 = self.cur
        self.lines.append(dict(t0=t0, t1=t0 + dur, who=who, to=to, text=text, cps=cps))
        for w in words:
            if w not in self.words:
                raise ScriptError(f'unknown word card {w!r}')
            self.cards.append(dict(type='word', id=w, t0=t0 + 0.3, t1=t0 + max(dur, 5.0) + 0.6))
        if who in self.cast and self.cast[who].get('era') and who not in self.nameplates_done:
            self.nameplates_done.add(who)
            self.cards.append(dict(type='name', id=who, t0=t0, t1=t0 + 5.5))
        self.cur = t0 + dur + GAP

    # ------------------------------------------------------------- commands
    def c_wait(self, c, s):
        return c + float(s)

    def c_title(self, c, dur='5.5'):
        self.title_t = (c, c + float(dur))
        return c

    def c_label(self, c, name):
        self.labels[name] = c
        return c

    mark = c_label

    def c_mark(self, c, name):
        return self.c_label(c, name)

    def c_short(self, c, n, which):
        n = int(n)
        w = self.shorts.setdefault(n, [])
        if which == 'start':
            w.append([c, None])
        else:
            w[-1][1] = c
        return c

    def c_chapter(self, c, *name):
        self.chapters.append((c, ' '.join(name)))
        return c

    def c_cook(self, c, s):
        t0 = max(c, self.haru_free)
        t = self.haru_walk(t0, POT_X)
        t1 = t + float(s)
        self._haru_seg(t, t1, lambda tt: dict(x=POT_X, pose='back', stir=True), POT_X)
        for k in range(int(float(s) / 0.9)):
            self._sfx('ladle', t + 0.4 + k * 0.9)
        return t1

    def c_haru(self, c, where, pose='front'):
        t0 = max(c, self.haru_free)
        k, x = self._where(where)
        if k == 'seat':
            x += 12
        t = self.haru_walk(t0, x)
        return t

    def c_bowhere(self, c):
        return self.c_bow(c, 'haru')

    def c_bow(self, c, who, dur='0.9'):
        d = float(dur)
        if who == 'haru':
            self._mod('haru', c, c + d, 'bow', True)
        else:
            self._mod(who, c, c + d, 'hdy', 2)
        return c + d

    def c_serve(self, c, who, dish='shoyu', cook='2.2'):
        t0 = max(c, self.haru_free)
        t = self.haru_walk(t0, POT_X)
        t1 = t + float(cook)
        self._haru_seg(t, t1, lambda tt: dict(x=POT_X, pose='back', stir=True), POT_X)
        for k in range(int(float(cook) / 0.9)):
            self._sfx('ladle', t + 0.4 + k * 0.9)
        floor = False
        if who in self.seat:
            bx = self.seat[who] + 12
            hx = bx + 3
        else:
            k, x = self._where(who)
            bx, hx = x, x
            floor = k == 'floor'
        if floor:
            hx = max(110, min(300, bx + 40))
        t2 = self.haru_walk(t1, hx, pose='carry', bowl=dish, speed=55)
        self._haru_seg(t2, t2 + 0.35, lambda tt, hx=hx: dict(x=hx, pose='carry', bowl=dish), hx)
        self._haru_seg(t2 + 0.35, t2 + 0.8, lambda tt, hx=hx: dict(x=hx, pose='place', bowl=dish), hx)
        tb = t2 + 0.8
        if floor:
            self.bowls.append(dict(who=who, x=bx, kind=dish, t0=tb, t1=1e9, floor=True, y=168))
            self._sfx('bowl_soft', tb)
        else:
            self.bowls.append(dict(who=who, x=bx, kind=dish, t0=tb, t1=1e9))
            self._sfx('bowl', tb)
        return tb

    def _bowl_of(self, who, t):
        for b in reversed(self.bowls):
            if b['who'] == who and b['t0'] <= t < b['t1']:
                return b
        for b in reversed(self.bowls):
            if b['who'] == who and b['t1'] > t:
                return b
        return None

    def c_finish(self, c, who, kind='empty'):
        b = self._bowl_of(who, c)
        if b:
            b['t1'] = c
            self.bowls.append(dict(b, kind=kind, t0=c, t1=1e9))
        return c

    def c_clear(self, c, who):
        b = self._bowl_of(who, c)
        if b:
            b['t1'] = c
        return c

    def c_eat(self, c, who, dur='6', slurps='2'):
        d = float(dur)
        self._mod(who, c, c + d, 'eat', True)
        n = int(slurps)
        for k in range(n):
            self._sfx('slurp_soft' if k % 2 else 'slurp', c + 0.8 + k * d / max(1, n), who=who)
        return c + d

    def c_slurp(self, c, who, loud='1'):
        self._mod(who, c, c + 1.4, 'eat', True)
        self._sfx('slurp' if loud == '1' else 'slurp_soft', c + 0.3, who=who)
        return c + 1.5

    def c_look(self, c, who, direction, dur='3'):
        d = float(dur)
        if who == 'haru':
            self._mod('haru', c, c + d, 'look', {'left': -1, 'right': 1}.get(direction, 0))
        else:
            self._mod(who, c, c + d, 'head', direction)
        return c + d if False else c

    def c_card(self, c, fid, dur=None):
        if fid not in self.facts:
            raise ScriptError(f'unknown fact card {fid!r}')
        f = self.facts[fid]
        d = float(dur) if dur else clamp(2.6 + len(f['body']) / 21.0, 7.0, 12.5)
        self.cards.append(dict(type='fact', id=fid, t0=c, t1=c + d))
        self._sfx('card', c)
        return c + d + 0.3

    def c_word(self, c, wid, dur='5.5'):
        if wid not in self.words:
            raise ScriptError(f'unknown word card {wid!r}')
        self.cards.append(dict(type='word', id=wid, t0=c, t1=c + float(dur)))
        return c

    def c_sign(self, c, who, dur='5.0'):
        t0 = max(c, self.haru_free)
        x = self.seat.get(who, 220) + 12
        if self.kind(who) in ('dog',):
            x = 140
        t = self.haru_walk(t0, x)
        self._haru_seg(t, t + 0.6, lambda tt, x=x: dict(x=x, pose='board'), x)
        self._haru_seg(t + 0.6, t + 0.6 + float(dur), lambda tt, x=x: dict(x=x, pose='board', signed=True), x)
        self._sfx('brush', t + 0.4)
        self.cards.append(dict(type='sign', id=who, t0=t + 0.6, t1=t + 0.6 + float(dur)))
        tb = t + 0.6 + float(dur)
        self.board_adds.append((tb, who))
        self._sfx('board', tb)
        return tb + 0.4

    def c_establish(self, c, view, caption='', dur='2.8'):
        d = float(dur)
        self.establish.append(dict(t0=c, t1=c + d, view=view, caption=caption))
        self._sfx('whoosh', c)
        return c + d

    def c_enter(self, c, who, where, **kw):
        view = kw.get('from', 'street')
        cap = kw.get('cap')
        t = c
        if cap:
            t = self.c_establish(t, view, cap, kw.get('estdur', '2.8')) + 0.3
        rattle = kw.get('rattle', '1') == '1'
        t_open = t + (0.75 if rattle else 0.05)
        kind = self.kind(who)
        k, x = self._where(where)
        speed = float(kw.get('speed', 50))
        tw = t_open + 0.3
        if kind == 'issun':
            arr = self.walk(who, [(DOOR_IN[0], 168), (62, 172), (x - 30, 172)], tw, speed=26, step='paddle', boat=True)
            self.door(t_open, arr - 2.0, view, rattle)
            # a hop up onto the counter
            def jump(tt, t0=arr, x0=x - 30, x1=x):
                u = clamp((tt - t0) / 0.7, 0, 1)
                return dict(who=who, mode='walk', x=x0 + (x1 - x0) * u, y=172 + (106 - 172) * u - 40 * math.sin(math.pi * u),
                            f=1, boat=False, on_counter=u >= 1.0)
            self._seg(who, arr, arr + 0.7, jump)
            self._sfx('boing', arr)
            end = arr + 0.7
            self.hold(who, end, 1e9, mode='sit', x=x, y=106, on_counter=True, f=1)
            self.seat[who] = x
            self.free[who] = end
            return end
        if kind == 'dog':
            arr = self.walk(who, [DOOR_IN, (62, 168), (x, 168)], tw, speed=40, step='paw', pose='walk')
            self.door(t_open, arr + 0.3, view, rattle)
            self.hold(who, arr, 1e9, mode='floor', x=x, y=168, f=1, pose='sit')
            self.seat[who] = x
            return arr + 0.2
        if k in ('floor', 'stand', 'x'):
            arr = self.walk(who, [DOOR_IN, (62, 170), (x, 170)], tw, speed=speed)
            self.door(t_open, min(arr, tw + 2.2), view, rattle)
            self.hold(who, arr, 1e9, mode='stand', x=x, y=170, f=1 if x > 62 else -1)
            self.seat[who] = x
            return arr + 0.2
        # an ordinary customer: through the door, along the floor, onto the stool
        arr = self.walk(who, [DOOR_IN, (62, FLOOR_Y), (x, FLOOR_Y)], tw, speed=speed,
                        step='step_geta' if who == 'kon' else 'step')
        self.door(t_open, min(tw + 1.9, arr), view, rattle)
        self.sit(who, x, arr)
        self.cam_hint.append((arr, arr + 60, x))
        return arr + 0.2

    def c_leave(self, c, who, **kw):
        view = kw.get('to', 'street')
        kind = self.kind(who)
        x = self.seat.get(who, 200)
        # close the seated segment
        self._close_from(who, c)
        if kind == 'issun':
            def jump(tt, t0=c, x0=x, x1=x - 30):
                u = clamp((tt - t0) / 0.7, 0, 1)
                return dict(who=who, mode='walk', x=x0 + (x1 - x0) * u, y=106 + (172 - 106) * u - 30 * math.sin(math.pi * u),
                            f=-1, boat=u >= 1.0)
            self._seg(who, c, c + 0.7, jump)
            arr = self.walk(who, [(x - 30, 172), (62, 172), (DOOR_IN[0], 168)], c + 0.8, speed=26, step='paddle', boat=True)
            self.door(arr - 1.6, arr + 0.6, view, rattle=False)
            self.hold(who, arr, arr + 1.2, mode='walk', x=DOOR_IN[0], y=147, f=-1, boat=True, outside=True)
            return arr + 0.6
        y0 = 168 if kind == 'dog' else FLOOR_Y
        t = c
        if kind not in ('dog', 'baku', 'zashiki', 'kasa') and self.cast[who].get('kind') != 'issun':
            t = self.hold(who, c, c + 0.3, mode='walk', x=x, y=y0, f=-1, phase=0)
        extra = dict(pose='walk') if kind == 'dog' else {}
        arr = self.walk(who, [(x, y0), (62, y0), (DOOR_IN[0], 147)], t, speed=float(kw.get('speed', 52)), **extra)
        self.door(arr - 1.8, arr + 1.8, view, rattle=False)
        self.hold(who, arr, arr + 1.2, mode='walk', x=DOOR_IN[0], y=147, f=1, phase=0, outside=True, **extra)

        def away(tt, t0=arr + 1.2):
            return dict(who=who, mode='walk', x=DOOR_IN[0] - (tt - t0) * 22, y=147, f=-1, phase=(tt - t0) * 5,
                        outside=True, **extra)
        self._seg(who, arr + 1.2, arr + 2.6, away)
        self.seat.pop(who, None)
        return arr + 0.3

    def _close_from(self, who, c):
        segs = self.segs.get(who, [])
        for i, (t0, t1, fn) in enumerate(segs):
            if t0 <= c < t1:
                segs[i] = (t0, c, fn)

    def c_move(self, c, who, where, speed='40'):
        """Walk a standing/floor character (or a hopping umbrella) somewhere."""
        k, x = self._where(where)
        kind = self.kind(who)
        self._close_from(who, c)
        cur = self._state_of(who, c - 1e-3) or dict(x=65, y=146)
        x0, y0 = cur.get('x', 65), cur.get('y', 170)
        if kind == 'kasa':
            y1 = 133 if k == 'seat' else 146
            n = max(2, int(abs(x - x0) / 14))
            dur = n * 0.45

            def hop(tt, t0=c, x0=x0, x1=x, y0=y0, y1=y1, n=n, dur=dur):
                u = clamp((tt - t0) / dur, 0, 1)
                ph = (u * n) % 1.0
                return dict(who=who, mode='stand', x=x0 + (x1 - x0) * u, y=y0 + (y1 - y0) * u,
                            hop=10 * math.sin(math.pi * ph), eye='open', tongue=8)
            self._seg(who, c, c + dur, hop)
            for i in range(n):
                self._sfx('hop', c + (i + 0.9) * dur / n)
            self.hold(who, c + dur, 1e9, mode='stand', x=x, y=y1, eye='open', tongue=8)
            self.seat[who] = x
            return c + dur
        yy = 168 if kind == 'dog' else 170
        extra = dict(pose='walk') if kind == 'dog' else {}
        arr = self.walk(who, [(x0, y0), (x, yy)], c, speed=float(speed), **extra)
        final = dict(mode='floor' if kind == 'dog' else 'stand', x=x, y=yy, f=1 if x >= x0 else -1)
        if kind == 'dog':
            final['pose'] = 'sit'
        self.hold(who, arr, 1e9, **final)
        self.seat[who] = x
        return arr

    def _state_of(self, who, t):
        best = None
        for t0, t1, fn in self.segs.get(who, []):
            if t0 <= t < t1 and (best is None or t0 >= best[0]):
                best = (t0, fn)
        return best[1](t) if best else None

    def c_wake(self, c, who, x='65', y='146'):
        """A yōkai that was part of the furniture opens its eye."""
        self.hold(who, c, 1e9, mode='stand', x=float(x), y=float(y), eye='open', tongue=8)
        self._sfx('pop', c)
        return c + 0.6

    def c_sleep(self, c, who):
        self._close_from(who, c)
        x = self.seat.get(who, 65)
        self.hold(who, c, 1e9, mode='stand', x=x, y=146, eye='closed', tongue=0)
        self._mod(who, c, 1e9, 'eye', 'closed')
        self._mod(who, c, 1e9, 'tongue', 0)
        return c

    def c_appear(self, c, who, where):
        k, x = self._where(where)
        if k == 'seat':
            self.sit(who, x, c)
        else:
            yy = 147 if self.kind(who) == 'zashiki' else 170
            self.hold(who, c, 1e9, mode='stand' if self.kind(who) != 'dog' else 'floor', x=x, y=yy, f=1)
            self.seat[who] = x
        self.props.append(dict(t0=c, t1=c + 0.8, name='smoke', x=x, y=120, k=0.6))
        self._sfx('sparkle', c)
        return c + 0.8

    def c_vanish(self, c, who):
        x = self.seat.get(who, 200)
        self._close_from(who, c)
        self.props.append(dict(t0=c, t1=c + 0.8, name='smoke', x=x, y=120, k=0.6))
        self._sfx('sparkle', c)
        self.seat.pop(who, None)
        return c + 0.8

    def c_stand(self, c, who):
        x = self.seat.get(who, 200)
        self._close_from(who, c)
        self.hold(who, c, 1e9, mode='stand', x=x, y=FLOOR_Y, f=1)
        return c + 0.3

    def c_sitdown(self, c, who, seat):
        k, x = self._where(seat)
        self._close_from(who, c)
        cur = self._state_of(who, c - 1e-3) or dict(x=x, y=FLOOR_Y)
        arr = self.walk(who, [(cur.get('x', x), FLOOR_Y), (x, FLOOR_Y)], c)
        self.sit(who, x, arr)
        return arr + 0.2

    def c_dance(self, c, who, x='160', dur='10'):
        d = float(dur)
        self._close_from(who, c)
        self.hold(who, c, c + d, mode='dance', x=float(x), y=172, beat=0.79)
        self.hold(who, c + d, 1e9, mode='stand', x=float(x), y=172, f=1)
        self.seat[who] = float(x)
        return c + d

    def c_transform(self, c, who, variant, dur='5'):
        d = float(dur)
        x = self.seat.get(who, 200)
        self.props.append(dict(t0=c, t1=c + 0.7, name='smoke', x=x, y=112, k=1.0))
        self.props.append(dict(t0=c - 0.6, t1=c, name='leaf', x=x, y=94))
        self._sfx('poof', c)
        if variant != 'none':
            self._mod(who, c + 0.25, c + d, 'variant', variant)
            self.props.append(dict(t0=c + d - 0.1, t1=c + d + 0.6, name='smoke', x=x, y=112, k=0.8))
            self._sfx('poof', c + d)
        return c + 0.7

    def c_set(self, c, who, key, val, dur='1e9'):
        v = _num(val)
        if v in ('true', 'yes'):
            v = True
        self._mod(who, c, c + float(dur), key, v)
        return c

    def c_spill(self, c, who):
        self._mod(who, c, c + 1e9, 'spilled', True)
        self._mod(who, c, c + 0.9, 'hdy', 3)
        self._sfx('splash', c)
        return c

    def c_refill(self, c, who):
        for i, m in enumerate(self.mods.get(who, [])):
            if m[2] == 'spilled' and m[0] <= c < m[1]:
                self.mods[who][i] = (m[0], c, m[2], m[3])
        self._sfx('pour', c - 0.6)
        return c

    def c_cho(self, c, *args, **kw):
        self.cho.append((c, self._cho_parse(list(args) + [f'{k}={v}' for k, v in kw.items()])))
        return c

    def _cho_parse(self, args):
        d = {}
        for a in args:
            k, _, v = a.partition('=')
            if k == 'look':
                d['look'] = tuple(int(q) for q in v.split(','))
            elif k in ('tongue', 'talk'):
                d[k] = v in ('1', 'true', 'yes')
            else:
                d[k] = v
        return d

    def c_prop(self, c, name, dur='1e9', **kw):
        d = dict(t0=c, t1=c + float(dur), name=name)
        for k, v in kw.items():
            d[k] = _num(v)
        if 'seat' in kw:
            d['x'] = SEATS[int(kw['seat']) - 1] + int(_num(kw.get('dx', 0)))
        self.props.append(d)
        return c

    def c_unprop(self, c, name):
        for p in self.props:
            if p['name'] == name and p['t0'] <= c < p['t1']:
                p['t1'] = c
        return c

    def c_staff(self, c, who, kind='staff'):
        self.staff.append([c, 1e9, self.seat.get(who, 200), kind, who])
        return c

    def c_unstaff(self, c, who):
        for s in self.staff:
            if s[4] == who and s[0] <= c < s[1]:
                s[1] = c
        return c

    def c_hatoff(self, c, who):
        self._mod(who, c, 1e9, 'hat_off', True)
        self.hat_stool.append([c, 1e9, self.seat.get(who, 200) + 32, who])
        return c

    def c_haton(self, c, who):
        for i, m in enumerate(self.mods.get(who, [])):
            if m[2] == 'hat_off' and m[0] <= c < m[1]:
                self.mods[who][i] = (m[0], c, m[2], m[3])
        for h in self.hat_stool:
            if h[3] == who and h[0] <= c < h[1]:
                h[1] = c
        return c

    def c_weather(self, c, w):
        self.weather.append((c, w))
        return c

    def c_flash(self, c, thunder='1'):
        self.flashes.append(c)
        if thunder == '1':
            self._sfx('thunder', c + 0.25)
        return c

    def c_light(self, c, x, y, r, col, k='0.8', dur='1e9'):
        rgb = tuple(float(v) for v in col.split(','))
        self.lights.append((c, c + float(dur), float(x), float(y), float(r), rgb, float(k)))
        return c

    def c_unlight(self, c):
        self.lights = [(t0, min(t1, c) if t0 <= c else t1, x, y, r, col, k) for (t0, t1, x, y, r, col, k) in self.lights]
        return c

    def c_sfx(self, c, name, **kw):
        self._sfx(name, c, **kw)
        return c

    def c_maneki(self, c, dur='3'):
        self.maneki.append((c, c + float(dur)))
        return c

    def c_boards(self, c, *who):
        for w in who:
            self.board_adds.append((c, w))
        return c

    def c_end(self, c, *text):
        self.end = c
        self.meta['end_text'] = ' '.join(text)
        return c + 14.0

    def c_cam(self, c, x, dur='1e9'):
        self.cam_hint.append((c, c + float(dur), float(x)))
        return c

    # ================================================================ frame state
    @staticmethod
    def _active(segs, t):
        best = None
        for t0, t1, fn in segs:
            if t0 <= t < t1 and (best is None or t0 >= best[0]):
                best = (t0, fn)
        return best[1](t) if best else None

    def _modval(self, mods, t, key, default=None):
        val, tb = default, -1e18
        for t0, t1, k, v in mods:
            if k == key and t0 <= t < t1 and t0 >= tb:
                val, tb = v, t0
        return val

    def door_state(self, t):
        o, outside, rattle = 0.0, 'street', 0
        for dv in self.doors:
            if dv['t0'] - 1.0 <= t <= dv['t1'] + 1.0:
                outside = dv['outside']
            if dv['t0'] <= t < dv['t1']:
                o = max(o, ease((t - dv['t0']) / 0.55))
            elif dv['t1'] <= t < dv['t1'] + 0.55:
                o = max(o, 1 - ease((t - dv['t1']) / 0.55))
        for tr in self.rattles:
            if tr <= t < tr + 0.45:
                rattle = 1 if int((t - tr) * 22) % 2 else 0
        return dict(open=o, outside=outside, rattle=rattle)

    def line_at(self, t):
        cur = None
        for ln in self.lines:
            if ln['t0'] <= t < ln['t1']:
                cur = ln
        return cur

    def weather_at(self, t):
        w = self.weather[0][1]
        for t0, ww in self.weather:
            if t0 <= t:
                w = ww
        return w

    def state(self, t):
        st = {}
        st['door'] = self.door_state(t)
        st['weather'] = self.weather_at(t)
        line = self.line_at(t)
        talking = None
        if line:
            shown = int((t - line['t0']) * line['cps'])
            talking = line['who'] if shown < len(line['text']) else None
        # Haru
        h = self._active(self.haru, t)
        if h is None:
            h = dict(x=self.haru_x_at(t), pose='front')
        h = dict(h)
        if self._modval(self.haru_mods, t, 'bow') and h['pose'] == 'front':
            h['pose'] = 'bow'
        h['blink'] = (t % 3.9) < 0.12
        h['mouth'] = 1 if talking == 'haru' and int(t * 9) % 2 == 0 else 0
        lk = self._modval(self.haru_mods, t, 'look')
        if lk is None and line and h['pose'] == 'front':
            other = line['to'] if line['who'] == 'haru' else line['who']
            ox = self._xof(other, t)
            if ox is not None:
                lk = -1 if ox < h['x'] - 6 else (1 if ox > h['x'] + 6 else 0)
        h['look'] = lk or 0
        st['haru'] = h
        # customers
        chars = []
        for who, segs in self.segs.items():
            c = self._active(segs, t)
            if not c:
                continue
            c = dict(c)
            mods = self.mods.get(who, [])
            c['mouth'] = 1 if talking == who and int(t * 9) % 2 == 0 else 0
            rng = (hash(who) % 97) / 97.0
            c['blink'] = ((t + rng * 3.7) % 4.1) < 0.12
            for key in ('variant', 'paper', 'spilled', 'hat_off', 'tails', 'perk', 'reach', 'wobble', 'eye', 'tongue',
                        'visible', 'pose_override'):
                v = self._modval(mods, t, key)
                if v is not None:
                    c[key] = v
            if c.get('visible') is False:
                continue
            if c['mode'] == 'sit' or c.get('on_counter'):
                head = 'back'
                if line and line['who'] == who:
                    head = self._face(who, line['to'], t, c['x'])
                elif line and line['to'] == who:
                    head = self._face(who, line['who'], t, c['x'])
                explicit = self._modval(mods, t, 'head')
                if explicit:
                    head = explicit
                c['head'] = head
                if self._modval(mods, t, 'eat') and head == 'back':
                    c['hdy'] = 1 if (t * 1.4) % 1.0 < 0.45 else 0
                hd = self._modval(mods, t, 'hdy')
                if hd is not None:
                    c['hdy'] = hd
                if c.get('paper') and (head != 'back'):
                    c['paper'] = False
                if c.get('on_counter') and head != 'back':
                    c['f'] = 1 if head == 'right' else -1
            if c['mode'] in ('stand', 'floor') and not c.get('outside'):
                tgt = None
                if line and line['who'] == who:
                    tgt = line['to']
                elif line and line['to'] == who:
                    tgt = line['who']
                tx = self._xof(tgt, t) if tgt else None
                if tx is not None and abs(tx - c['x']) > 4:
                    c['f'] = 1 if tx > c['x'] else -1
                explicit = self._modval(mods, t, 'head')
                if explicit in ('left', 'right'):
                    c['f'] = 1 if explicit == 'right' else -1
                if talking == who:
                    c['mouth'] = 1 if int(t * 9) % 2 == 0 else 0
            if c['mode'] == 'walk' and talking == who:
                c['mouth'] = 1 if int(t * 9) % 2 == 0 else 0
            chars.append(c)
        st['chars'] = chars
        # noren lifts as someone passes under it
        lift = [0, 0, 0]
        for c in chars:
            if c['mode'] == 'walk' and c.get('y', 170) < 160:
                for i, cxp in enumerate((16, 30, 44)):
                    k = max(0.0, 1 - abs(c['x'] - cxp) / 14.0) * max(0.0, 1 - (c.get('y', 170) - 146) / 14.0)
                    lift[i] = max(lift[i], 13 * k)
        st['noren'] = dict(lift=lift, gust=1.0 if st['door']['open'] > 0.5 and st['door']['outside'] in
                           ('storm', 'snow_mtn') else 0.0)
        st['bowls'] = [dict(x=b['x'], kind=b['kind'], floor=b.get('floor', False), y=b.get('y', 168),
                            steam=0 if b['kind'] in ('empty', 'cold', 'frozen') else clamp(1.0 - (t - b['t0']) / 50.0, 0.25, 1.0))
                       for b in self.bowls if b['t0'] <= t < b['t1']]
        st['props'] = [p for p in self.props if p['t0'] <= t < p['t1']]
        st['props'] = [self._animate_prop(p, t) for p in st['props']]
        st['staff'] = [(s[2], s[3]) for s in self.staff if s[0] <= t < s[1]]
        hs = [h_[2] for h_ in self.hat_stool if h_[0] <= t < h_[1]]
        st['hat_stool'] = hs[0] if hs else None
        # boards on the wall
        boards = [(self.cast[w]['mark'], 0.0) for w in self.boards0]
        for tb, w in self.board_adds:
            if tb <= t:
                boards.append((self.cast[w]['mark'], clamp(1.0 - (t - tb) / 3.0, 0, 1)))
        st['boards'] = boards[:35]
        # Chō
        cs = dict(eye='closed', look=(0, 0), tongue=False)
        for tc, kw in self.cho:
            if tc <= t:
                cs.update(kw)
        sway = 0.0
        for dv in self.doors:
            for te in (dv['t0'], dv['t1']):
                if te <= t < te + 3:
                    sway += 1.6 * math.sin((t - te) * 6) * math.exp(-(t - te) * 1.2)
        cs['sway'] = sway
        if cs['eye'] in ('open', 'wide') and (t % 4.3) < 0.1:
            cs['eye'] = 'closed'
        if talking == 'cho':
            cs['talk'] = int(t * 8) % 2 == 0
        st['cho'] = cs
        st['maneki'] = any(a <= t < b for a, b in self.maneki)
        fl = 0.0
        for tf in self.flashes:
            if tf <= t < tf + 0.5:
                fl = max(fl, (1 - (t - tf) / 0.5) * (1.0 if (t - tf) < 0.08 or 0.16 < (t - tf) < 0.24 else 0.5))
        st['flash'] = fl
        st['lights'] = [(x, y, r, col, k) for (t0, t1, x, y, r, col, k) in self.lights if t0 <= t < t1]
        for e in self.establish:
            if e['t0'] <= t < e['t1']:
                a = min(1.0, (t - e['t0']) / 0.25, (e['t1'] - t) / 0.25)
                st['establish'] = dict(view=e['view'], caption=e['caption'], a=1.0 if a > 0.5 else a * 2)
        # overlay information
        if line:
            st['line'] = dict(who=line['who'], text=line['text'], shown=int((t - line['t0']) * line['cps']))
        tops = []
        for cd in self.cards:
            if cd['t0'] <= t < cd['t1']:
                u = min(ease((t - cd['t0']) / 0.3), ease((cd['t1'] - t) / 0.3))
                tops.append(dict(cd, u=u))
        st['cards'] = tops
        if self.title_t and self.title_t[0] <= t <= self.title_t[1]:
            a, b = self.title_t
            st['title'] = min(ease((t - a) / 0.8), ease((b - t) / 0.8))
        if self.end is not None and t >= self.end:
            st['end'] = ease((t - self.end) / 1.0)
            st['dim'] = st['end']
        return st

    def _animate_prop(self, p, t):
        if p['name'] == 'smoke':
            u = (t - p['t0']) / max(0.01, p['t1'] - p['t0'])
            return dict(p, k=p.get('k', 1.0) * (0.5 + u) * (1 - u) * 2)
        if p['name'] == 'box' and 'opening' in p:
            u = clamp((t - p['t0']) / 1.0, 0, 1)
            return dict(p, open=u)
        if p['name'] == 'bubble' and 'shrink' in p:
            u = clamp((t - p['t0'] - float(p['shrink'])) / 1.2, 0, 1)
            return dict(p, k=1.0 - u)
        if p['name'] == 'stack' and 'rate' in p:
            n = min(p.get('n', 47), int((t - p['t0']) * float(p['rate'])))
            return dict(p, n=n)
        if p['name'] == 'paper' and 'draw' in p:
            return dict(p, wave=clamp((t - p['t0']) / float(p['draw']), 0, 1))
        return p

    def _xof(self, who, t):
        if who is None:
            return None
        if who == 'haru':
            return self.haru_x_at(t)
        if who == 'cho':
            return 75
        c = self._active(self.segs.get(who, []), t)
        return c['x'] if c else None

    def _face(self, who, target, t, x):
        tx = self._xof(target, t)
        if tx is None:
            return 'right'
        return 'right' if tx >= x else 'left'

    # ================================================================ outputs
    def teaser_range(self):
        if not self.teaser:
            return None
        lab, dur = self.teaser
        t0 = self.labels[lab]
        return (t0, t0 + dur)

    def short_windows(self, n):
        return [tuple(w) for w in self.shorts[n]]
