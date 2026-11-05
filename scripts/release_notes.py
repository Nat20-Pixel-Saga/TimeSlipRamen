"""Release notes for a release (week-1 ... week-4, channel-kit), from docs/upload-schedule.json."""
import datetime as dt
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TITLES = {
    'channel-kit': 'Channel kit',
    'week-1': 'Week 1 · Mon 16 - Sun 22 Nov',
    'week-2': 'Week 2 · Mon 23 - Sun 29 Nov',
    'week-3': 'Week 3 · Mon 30 Nov - Sun 6 Dec',
    'week-4': 'Week 4 · Mon 7 - Sun 13 Dec (season finale)',
}
INTROS = {
    'channel-kit': [
        "Everything for setting up the channel: `logo_800.png`, `banner_2560x1440.png`, `watermark_150.png`, the "
        "channel description and keywords (`description.md`), and the trailer with its thumbnail.", "",
        "Publish the trailer on **Sat 14 Nov at 17:00** and set it as the channel trailer for new visitors."],
}
WEEK_INTRO = [
    "Episodes (Mon, Wed, Fri at 17:00 CET) with thumbnails A (`-thumb-A.png`, the visitor and hook words) and "
    "B (`-thumb-B.png`, the shop, no words) for Test & compare; Shorts every day at 19:00, each with a vertical "
    "thumbnail (`-thumb.png`, 1080x1920).", "",
    "Titles A and B, descriptions (chapters, facts and sources), pinned comments and playlists for every upload "
    "are in [`docs/upload-schedule.md`](https://github.com/" + os.environ.get('GITHUB_REPOSITORY', 'Nat20-Pixel-Saga/TimeSlipRamen')
    + "/blob/main/docs/upload-schedule.md)."]


def title(tag):
    return TITLES.get(tag, tag)


def notes(tag):
    with open(os.path.join(ROOT, 'docs', 'upload-schedule.json'), encoding='utf-8') as f:
        its = [i for i in json.load(f) if i['release'] == tag]
    lines = INTROS.get(tag, WEEK_INTRO) + ['', '| When (CET) | Upload | Title | File |', '|---|---|---|---|']
    for i in its:
        d = dt.date.fromisoformat(i['date']).strftime('%a %d %b')
        t = i['title'].replace('|', r'\|')
        lines.append(f"| {d} {i['time']} | {i['id']} | {t} | `{i['file']}` |")
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--title':
        print(title(sys.argv[2]))
    else:
        print(notes(sys.argv[1]))
