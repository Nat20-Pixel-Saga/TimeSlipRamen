"""Timeline -> MP4.  Landscape episodes (1920x1080) and vertical Shorts (1080x1920), 30 fps.

Frames are drawn at 640x360 (or 360x640) and scaled x3 by ffmpeg with nearest neighbour.
Work is split into parts rendered in parallel processes, joined with the concat demuxer,
and the sound (mixed in numpy) is added with a two-pass loudness normalisation.
"""
import json
import math
import multiprocessing as mp
import os
import subprocess
import time

import numpy as np
from PIL import Image, ImageDraw

from . import audio as A
from .gfx import FPS, clamp, C
from .shop import Shop
from .ui import Overlay

FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')


def seigaiha(w, h, c1=(30, 34, 66), c2=(44, 52, 96), c3=(60, 70, 120)):
    """A wave-scale pattern for the bands above and below the scene in Shorts."""
    im = Image.new('RGB', (w, h), c1)
    d = ImageDraw.Draw(im)
    r = 12
    for row in range(-1, h // (r // 2) + 2):
        y = row * r // 2
        off = (row % 2) * r
        for x in range(-r, w + r, 2 * r):
            for k, col in ((r, c2), (r - 3, c1), (r - 6, c3), (r - 9, c1)):
                d.ellipse([x + off - k, y - k, x + off + k, y + k], outline=col)
    return np.asarray(im).astype(np.uint8)


class Framer:
    def __init__(self, tl, fmt, words, facts, plan, hook=None, cam=None, subject=None):
        self.tl, self.fmt, self.plan, self.hook, self.subject = tl, fmt, plan, hook, subject
        self.shop = Shop(tl.cast)
        self.ov = Overlay(fmt, tl.cast, words, facts, tl.meta)
        self.cam = cam
        self.cum = [0.0]
        for a, b in plan:
            self.cum.append(self.cum[-1] + (b - a))
        if fmt == 'short':
            band = seigaiha(360, 640)
            self.base = band.copy()
            lab = Image.fromarray(self.base)
            from .gfx import text_img
            t1 = text_img('TIMESLIP RAMEN · タイムスリップ・ラーメン', (240, 220, 180), shadow=(20, 16, 30))
            lab = lab.convert('RGBA')
            lab.alpha_composite(t1, ((360 - t1.width) // 2, 597))
            t2 = text_img('full episode on the channel', (190, 196, 220), shadow=(20, 16, 30))
            lab.alpha_composite(t2, ((360 - t2.width) // 2, 616))
            self.base = np.asarray(lab.convert('RGB')).copy()
            self.path = self._cam_path()

    def _cam_path(self, step=0.1):
        """Shorts: a camera that follows whoever is talking, keeping the visitor in frame when
        the speaker sits close enough, panning smoothly within a window and cutting between them."""
        tl, subj = self.tl, (self.cam if self.cam is not None else 220)
        n = int(self.cum[-1] / step) + 2
        tgt, out, cur = subj, np.zeros(n), None
        cuts = {int(round(c / step)) for c in self.cum[1:-1]}
        for i in range(n):
            to = min(i * step, self.cum[-1] - 1e-3)
            t = self.src_time(to)
            sx = tl._xof(self.subject, t) if self.subject else None
            s0 = sx if sx is not None else subj
            ln = next((l for l in tl.lines if l['t0'] - 0.3 <= t < l['t1']), None)
            if ln:
                xa = tl._xof(ln['who'], t)
                xb = tl._xof(ln['to'], t) if ln.get('to') else None
                if xa is not None:
                    if xb is not None and abs(xa - xb) <= 96:
                        tgt = (xa + xb) / 2
                    elif abs(xa - s0) <= 96:
                        tgt = (xa + s0) / 2
                    else:
                        tgt = xa
            elif i == 0 or not any(l['t1'] + 1.2 > t >= l['t0'] for l in tl.lines):
                tgt = s0  # nobody has spoken for a moment: back to the visitor
            tgt = clamp(tgt, 60, 260)
            if cur is None or i in cuts:
                cur = tgt
            else:
                d = (tgt - cur) * (1 - math.exp(-step / 0.4))
                cur += clamp(d, -160 * step, 160 * step)
            out[i] = cur
        return out

    def cam_at(self, to):
        f = to / 0.1
        i = int(clamp(f, 0, len(self.path) - 2))
        u = clamp(f - i, 0, 1)
        return self.path[i] * (1 - u) + self.path[i + 1] * u

    def src_time(self, to):
        for i, (a, b) in enumerate(self.plan):
            if to < self.cum[i + 1] or i == len(self.plan) - 1:
                return a + (to - self.cum[i])
        return self.plan[-1][1]

    def frame(self, to):
        t = self.src_time(to)
        st = self.tl.state(t)
        world = self.shop.render(st, t)
        w8 = (world * 255 + 0.5).astype(np.uint8)
        if self.fmt == 'landscape':
            up = np.repeat(np.repeat(w8, 2, 0), 2, 1)
            ui = self.ov.draw(st, t)
            return composite(up, ui)
        cx = self.cam_at(to)
        x0 = int(clamp(round(cx - 60), 0, 200))
        crop = w8[:, x0:x0 + 120]
        up = np.repeat(np.repeat(crop, 3, 0), 3, 1)
        out = self.base.copy()
        out[50:590] = up
        ha = 0.0
        if self.hook and to < 3.0:
            ha = 1.0 if to < 2.6 else (3.0 - to) / 0.4
        ui = self.ov.draw(st, t, hook=self.hook, hook_a=ha)
        return composite(out, ui)


def composite(base, ui):
    u = np.asarray(ui).astype(np.float32)
    a = u[:, :, 3:4] / 255.0
    f = base.astype(np.float32) * (1 - a) + u[:, :, :3] * a
    return f.astype(np.uint8)


_JOB = {}


def _worker(k, f0, f1, path):
    j = _JOB
    fr = Framer(j['tl'], j['fmt'], j['words'], j['facts'], j['plan'], j.get('hook'), j.get('cam'),
                j.get('subject'))
    W_, H_ = (640, 360) if j['fmt'] == 'landscape' else (360, 640)
    OW, OH = W_ * 3, H_ * 3
    tmp = path[:-4] + '.tmp.mp4'
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}',
           '-r', str(FPS), '-i', '-', '-vf', f'scale={OW}:{OH}:flags=neighbor', '-c:v', 'libx264',
           '-preset', j['preset'], '-crf', str(j['crf']), '-g', str(FPS * 4), '-pix_fmt', 'yuv420p',
           '-threads', '2', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ts = time.time()
    for fi in range(f0, f1):
        p.stdin.write(fr.frame(fi / FPS).tobytes())
        if k == 0 and (fi - f0) % (FPS * 60) == 0 and fi > f0:
            el = time.time() - ts
            done = (fi - f0) / (f1 - f0)
            print(f'    part0 {done * 100:.0f}%  {el / 60:.1f} min, eta {el / done * (1 - done) / 60:.1f} min', flush=True)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f'ffmpeg failed on part {k}')
    os.replace(tmp, path)


def loudnorm(wav, target):
    r = subprocess.run([FFMPEG, '-hide_banner', '-i', wav, '-af', f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    return (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
            f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")


def render(tl, out_path, fmt, words, facts, plan, music, music_start=0.0, music_at=0.0, hook=None, cam=None, subject=None,
           workers=2, crf=20, preset='veryfast', target_lufs=-16, log=print, seed=1):
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    base = out_path[:-4]
    t0 = time.time()
    total = sum(b - a for a, b in plan)
    n = int(round(total * FPS))
    st = A.mix_plan(tl, plan, music, music_start=music_start, music_at=music_at, seed=seed)
    wav = base + '.wav'
    A.write_wav(wav, st)
    log(f'  audio {total:.1f}s in {time.time() - t0:.0f}s')
    _JOB.clear()
    _JOB.update(tl=tl, fmt=fmt, words=words, facts=facts, plan=plan, hook=hook, cam=cam, subject=subject, crf=crf,
                preset=preset)
    nseg = max(1, workers)
    bounds = [int(n * k / nseg) for k in range(nseg + 1)]
    parts = [f'{base}.part{k}.mp4' for k in range(nseg)]
    t1 = time.time()
    ctx = mp.get_context('fork')
    procs = [ctx.Process(target=_worker, args=(k, bounds[k], bounds[k + 1], parts[k])) for k in range(nseg)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
        if p.exitcode != 0:
            raise SystemExit('a render worker failed')
    log(f'  frames in {(time.time() - t1) / 60:.1f} min')
    lst = base + '.txt'
    with open(lst, 'w') as f:
        for s in parts:
            f.write(f"file '{os.path.abspath(s)}'\n")
    af = loudnorm(wav, target_lufs)
    tmp = base + '.tmp.mp4'
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af, '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, out_path)
    for s in parts + [lst, wav]:
        if os.path.exists(s):
            os.remove(s)
    log(f'  {os.path.basename(out_path)} done in {(time.time() - t0) / 60:.1f} min')
    return out_path


def still(tl, t, fmt, words, facts, cam=None, hook=None, subject=None, plan=None, to=None):
    """One frame. For Shorts pass plan= and to= (output time) to see the moving camera."""
    fr = Framer(tl, fmt, words, facts, plan or [(t, t + 1)], hook=hook, cam=cam, subject=subject)
    return Image.fromarray(fr.frame(0.0 if to is None else to))
