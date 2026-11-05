"""Expand a render request into a GitHub Actions matrix, from docs/upload-schedule.json (so the
plan job needs nothing but Python).

    python3 scripts/plan_jobs.py week-1            # everything uploaded Mon 16 - Sun 22 Nov
    python3 scripts/plan_jobs.py channel-kit       # the trailer (logo, banner, watermark are committed)
    python3 scripts/plan_jobs.py all
    python3 scripts/plan_jobs.py ep03 short12 trailer
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def all_items():
    with open(os.path.join(ROOT, 'docs', 'upload-schedule.json'), encoding='utf-8') as f:
        return [(i['id'], i['release']) for i in json.load(f)]


def expand(req):
    items = all_items()
    want = []
    for tok in req.split():
        if tok == 'all':
            want += items
        elif tok.startswith('week-') or tok == 'channel-kit':
            want += [i for i in items if i[1] == tok]
        else:
            hit = [i for i in items if i[0] == tok]
            if not hit:
                raise SystemExit(f'unknown item: {tok}')
            want += hit
    seen, out = set(), []
    for it in want:
        if it[0] not in seen:
            seen.add(it[0])
            out.append(it)
    # long videos first so the matrix finishes sooner
    out.sort(key=lambda x: (not x[0].startswith(('ep', 'trailer')), x[0]))
    return out


if __name__ == '__main__':
    print(json.dumps({'include': [{'item': i, 'release': r} for i, r in expand(' '.join(sys.argv[1:]))]}))
