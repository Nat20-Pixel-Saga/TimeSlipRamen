"""Write the upload plan for Season 1: docs/upload-schedule.json, .csv and .md, with every title
(A/B), description (chapters, visitors, facts with sources), pinned comment, playlist and file.

    python3 scripts/make_schedule.py
"""
import csv
import datetime as dt
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from content import meta as M  # noqa: E402
from content import shorts as SH  # noqa: E402
from content.cast import CAST  # noqa: E402
from content.facts import FACTS  # noqa: E402
from content.words import WORDS  # noqa: E402
from content.season import load_episode, EP_VISITORS  # noqa: E402
from engine.thumbs import short_moment  # noqa: E402

DOCS = os.path.join(ROOT, 'docs')
SEASON_START = dt.date(2026, 11, 16)


def week_of(date):
    d = dt.date.fromisoformat(date)
    return max(1, (d - SEASON_START).days // 7 + 1)


def ts(sec):
    sec = int(round(sec))
    return f'{sec // 60}:{sec % 60:02d}'


def fact_title(fid):
    """'松尾芭蕉  MATSUO BASHŌ · poet, 1644–1694' -> 'Matsuo Bashō · poet, 1644–1694'"""
    t = FACTS[fid]['title']
    if '  ' in t:
        t = t.split('  ', 1)[1]
    head, _, tail = t.partition(' · ')
    head = ' '.join(w.capitalize() if w.isupper() else w for w in head.split())
    return head + (f' · {tail}' if tail else '')


def cards_in(tl, kind, windows=None):
    out = []
    for c in tl.cards:
        if c['type'] != kind:
            continue
        if windows and not any(a <= c['t0'] < b for a, b in windows):
            continue
        if c['id'] not in out:
            out.append(c['id'])
    return out


def facts_block(fids):
    lines = []
    for fid in fids:
        f = FACTS[fid]
        lines.append(f'· {fact_title(fid)}: {f["body"]}')
        for title, url in f['sources']:
            lines.append(f'  Source: {title}, {url}')
    return lines


def words_block(wids):
    return [f'· {WORDS[w]["jp"]} {WORDS[w]["romaji"]}: {WORDS[w]["meaning"]}' for w in wids if w in WORDS]


def episode_item(n, date):
    tl = load_episode(n)
    a, b, hook, pinned = M.EPISODES_META[n]
    tr = tl.teaser_range()
    lead = (tr[1] - tr[0]) if tr else 0.0
    dur = tl.duration + lead
    chapters = [(0.0, 'Cold open')] + [(t + lead, name) for t, name in tl.chapters]
    vis = EP_VISITORS[n]
    d = [hook, '', 'Tonight at the counter:']
    d += [f'· {M.VISITOR_LINES[v]}' for v in vis]
    d += ['', 'Chapters'] + [f'{ts(t)} {name}' for t, name in chapters]
    d += ['', '豆知識 · Facts on screen (with sources)'] + facts_block(cards_in(tl, 'fact'))
    d += ['', 'Words on screen'] + words_block(cards_in(tl, 'word'))
    d += ['', f'{M.CHANNEL} is a pixel-art ramen shop on a rainy street corner whose door opens onto any century. '
              'Haru keeps the broth hot, Kon the fox keeps trying to look human, Mika studies for her exams and '
              'Gen-san refuses to believe any of it.',
          'New episodes Monday, Wednesday and Friday at 17:00 (CET), and a new Short every day at 19:00.',
          'Music: original, generated for the channel. Facts checked November 2026; corrections welcome in the '
          'comments.', '', M.HASHTAGS]
    pl = [M.PLAYLISTS[0]['name']]
    if any(CAST[v].get('kind') != 'person' or v in ('kappa', 'tanuki', 'kasa', 'issun', 'urashima', 'kaguya', 'raijin',
                                                    'zashiki', 'yuki', 'baku', 'grandma') for v in vis):
        pl.append(M.PLAYLISTS[2]['name'])
    if any(v in ('basho', 'musashi', 'hokusai', 'mitsukuni', 'gennai', 'hachiko', 'seimei', 'ino', 'murasaki', 'sei',
                 'shibusawa', 'tsuda', 'kitasato', 'michizane', 'hanzo', 'oishi', 'okuni') for v in vis):
        pl.append(M.PLAYLISTS[3]['name'])
    sid = f'ep{n:02d}'
    return dict(id=sid, kind='episode', n=n, date=date.isoformat(), time=M.EP_TIME,
                release=f'week-{week_of(date.isoformat())}', file=f'timeslip-ramen-{sid}.mp4',
                thumb_a=f'timeslip-ramen-{sid}-thumb-A.png', thumb_b=f'timeslip-ramen-{sid}-thumb-B.png',
                title=f'{a} | {M.CHANNEL} Ep. {n}', title_b=f'{b} (Ep. {n})', duration=ts(dur),
                visitors=[CAST[v]['name'] for v in vis], description='\n'.join(d), pinned=pinned,
                playlists=pl, chapters=[f'{ts(t)} {name}' for t, name in chapters])


def short_item(sh, date):
    n = sh['n']
    tl = load_episode(sh['ep'])
    win = tl.short_windows(n)
    dur = sum(b - a for a, b in win)
    ep_title = M.EPISODES_META[sh['ep']][0]
    d = [f'{M.VISITOR_LINES[sh["who"]][0].upper()}{M.VISITOR_LINES[sh["who"]][1:]}.',
         f'From Episode {sh["ep"]}, "{ep_title}". The full episode is on the channel.', '']
    fids = cards_in(tl, 'fact', win)
    if fids:
        d += ['豆知識'] + facts_block(fids) + ['']
    d += [SH_TAGS]
    sid = f'short{n:02d}'
    _, frame = short_moment(tl, sh['who'], win)
    return dict(id=sid, kind='short', n=n, ep=sh['ep'], date=date.isoformat(), time=M.SHORT_TIME,
                release=f'week-{week_of(date.isoformat())}', file=f'timeslip-ramen-{sid}.mp4',
                title=sh['title'], hook=sh['hook'], duration=ts(dur), visitors=[CAST[sh['who']]['name']],
                description='\n'.join(d), related=f'ep{sh["ep"]:02d}', playlists=[M.PLAYLISTS[1]['name']],
                thumb=f'timeslip-ramen-{sid}-thumb.png', thumb_frame=f'{int(frame) // 60}:{frame % 60:04.1f}')


SH_TAGS = M.SHORT_TAGS


def trailer_item():
    t = M.TRAILER
    d = ['A ramen shop on a rainy corner. The door opens onto any century, and tonight anyone from Japanese history '
         'or folklore might walk in: poets, samurai, a kappa, the thunder god, the people on your banknotes.', '',
         f'{M.SEASON} starts Monday 16 November 2026: new episodes Monday, Wednesday and Friday at 17:00 (CET), '
         'and a new Short every day at 19:00.', '', M.HASHTAGS]
    return dict(id='trailer', kind='trailer', date=t['date'], time=t['time'], release='channel-kit',
                file='timeslip-ramen-trailer.mp4', thumb_a='timeslip-ramen-trailer-thumb-A.png',
                title=t['title'], title_b=t['title_b'], description='\n'.join(d),
                pinned='Pull up a stool. Who would you most like to see walk in?', playlists=[],
                note='Set as the channel trailer for new visitors (Customisation > Layout).')


def build():
    items = [trailer_item()]
    for n, d in enumerate(M.episode_dates(), 1):
        items.append(episode_item(n, d))
    for sh, d in zip(SH.all_shorts(), M.short_dates()):
        items.append(short_item(sh, d))
    items.sort(key=lambda i: (i['date'], i['time']))
    return items


def weekday(date):
    return dt.date.fromisoformat(date).strftime('%a %d %b')


def write(items):
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, 'upload-schedule.json'), 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DOCS, 'upload-schedule.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['date', 'time', 'kind', 'id', 'release', 'file', 'title_A', 'title_B', 'thumb_A', 'thumb_B',
                    'duration', 'playlists', 'pinned_comment'])
        for i in items:
            w.writerow([i['date'], i['time'], i['kind'], i['id'], i['release'], i['file'], i['title'],
                        i.get('title_b', ''), i.get('thumb_a', i.get('thumb', '')), i.get('thumb_b', ''), i.get('duration', ''),
                        ' | '.join(i.get('playlists', [])), i.get('pinned', '')])
    md = [f'# {M.CHANNEL} · {M.SEASON}: upload schedule', '',
          f'All times {M.TZ} (CET). Episodes Mon/Wed/Fri {M.EP_TIME}, Shorts daily {M.SHORT_TIME}, from '
          'Mon 16 Nov to Sun 13 Dec 2026. Files are in the GitHub releases named in the "release" column. '
          'Generated by `scripts/make_schedule.py` from `content/meta.py`; do not edit by hand.', '',
          '**A/B test** (YouTube Studio > the video > Test & compare): upload with title A and thumbnail A, then '
          'add thumbnail B (and title B, where Studio offers title tests). Let it run until Studio picks a winner, '
          'usually one to two weeks.', '',
          '**Shorts thumbnails** (1080x1920, words in the middle band so they survive the wider crop some pages '
          'use): YouTube is rolling custom Shorts thumbnails out to Partner Program channels first, and only in '
          'Studio on desktop; there is no A/B test for Shorts. Until the option appears, choose the frame listed '
          'for each Short (it is the same picture).', '',
          '| Date | Time | Item | Title (A) | Release |', '|---|---|---|---|---|']
    for i in items:
        t = i['title'].replace('|', r'\|')
        md.append(f'| {weekday(i["date"])} | {i["time"]} | {i["id"]} | {t} | {i["release"]} |')
    md += ['', '## Playlists', '']
    for p in M.PLAYLISTS:
        md.append(f'- **{p["name"]}** ({p["items"]}): {p["description"]}')
    md += ['', '## Every upload', '']
    for i in items:
        md += [f'### {weekday(i["date"])} {i["time"]} · {i["id"]}', '',
               f'- File: `{i["file"]}` (release `{i["release"]}`)' + (f', {i["duration"]}' if i.get('duration') else '')]
        if i.get('title_b'):
            md += [f'- Title A: {i["title"]}', f'- Title B: {i["title_b"]}']
        else:
            md += [f'- Title: {i["title"]}']
        if i.get('thumb'):
            md += [f'- Thumbnail: `{i["thumb"]}` (Studio on desktop). If Studio doesn\'t offer a custom thumbnail '
                   f'for Shorts yet, pick the frame at {i["thumb_frame"]} (same picture, with the dialogue box)']
        if i.get('thumb_a'):
            md += [f'- Thumbnails: `{i["thumb_a"]}` (A)' + (f', `{i["thumb_b"]}` (B)' if i.get('thumb_b') else '')]
        if i.get('hook'):
            md += [f'- On-screen hook: "{i["hook"]}"; link the related video: {i["related"]}']
        if i.get('pinned'):
            md += [f'- Pinned comment: {i["pinned"]}']
        if i.get('playlists'):
            md += [f'- Playlists: {", ".join(i["playlists"])}']
        if i.get('note'):
            md += [f'- Note: {i["note"]}']
        md += ['', '```', i['description'], '```', '']
    with open(os.path.join(DOCS, 'upload-schedule.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))


if __name__ == '__main__':
    its = build()
    write(its)
    print(f'{len(its)} uploads written to docs/upload-schedule.(md|csv|json)')
