"""The channel trailer (Sat 14 Nov 2026): content/scripts/trailer.txt, rendered landscape."""
import os

from engine.director import Timeline
from engine.render import render
from .cast import CAST
from .words import WORDS
from .facts import FACTS

HERE = os.path.dirname(os.path.abspath(__file__))


def load_trailer():
    with open(os.path.join(HERE, 'scripts', 'trailer.txt'), encoding='utf-8') as f:
        text = f.read()
    return Timeline(CAST, WORDS, FACTS, boards0=[], name='trailer').load(text)


def render_trailer(out, workers):
    tl = load_trailer()
    path = os.path.join(out, 'timeslip-ramen-trailer.mp4')
    render(tl, path, 'landscape', WORDS, FACTS, [(0.0, tl.duration)], tl.meta['music'], workers=workers,
           target_lufs=-16, seed=7)
    return path
