"""Season 1 · Rainy Nights (16 Nov - 13 Dec 2026): 12 episodes, 28 Shorts, a trailer.

This file is the source of truth for titles (A/B), descriptions, Shorts and the schedule;
scripts live in content/scripts/epNN.txt.
"""
import os

from engine.director import Timeline
from .cast import CAST, VISITORS
from .words import WORDS
from .facts import FACTS

HERE = os.path.dirname(os.path.abspath(__file__))

# visitors per episode, in order of arrival (each signs the wall)
EP_VISITORS = {
    1: ['basho', 'kappa'], 2: ['musashi', 'tanuki'], 3: ['hokusai', 'kasa', 'issun'],
    4: ['mitsukuni', 'gennai'], 5: ['hachiko', 'urashima'], 6: ['kaguya', 'raijin', 'zashiki'],
    7: ['seimei', 'ino'], 8: ['murasaki', 'sei'], 9: ['shibusawa', 'tsuda', 'kitasato'],
    10: ['yuki', 'michizane'], 11: ['baku', 'hanzo'], 12: ['oishi', 'grandma', 'okuni'],
}


def boards_before(n):
    out = []
    for k in range(1, n):
        out += EP_VISITORS.get(k, [])
    return out


def load_episode(n):
    path = os.path.join(HERE, 'scripts', f'ep{n:02d}.txt')
    with open(path, encoding='utf-8') as f:
        text = f.read()
    tl = Timeline(CAST, WORDS, FACTS, boards0=boards_before(n), name=f'ep{n:02d}')
    return tl.load(text)
