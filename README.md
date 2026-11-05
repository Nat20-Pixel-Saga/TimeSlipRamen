# Timeslip Ramen

A tiny pixel-art ramen shop on a rainy street corner, whose door opens onto any century. Poets, samurai,
yōkai, gods and the people on your banknotes walk in for a bowl, sign the wall, and leave a little Japanese
history or folklore behind. Everything is rendered in Python: the pixel art, the lighting and weather, the
characters, the on-screen fact and word cards, and the original lo-fi music.

**Season 1 · Rainy Nights** runs from Monday 16 November to Sunday 13 December 2026:
12 episodes (Mon, Wed, Fri at 17:00 CET), 28 Shorts (every day at 19:00) and a channel trailer (Sat 14 Nov).

- **Finished videos and thumbnails** are attached to the [Releases](../../releases): `channel-kit`, `week-1` … `week-4`.
- **What to upload, when, with which titles (A and B), descriptions, pinned comments and playlists:**
  [`docs/upload-schedule.md`](docs/upload-schedule.md) (also `.csv` and `.json`).
- **Channel setup** (name, handle, description, keywords, layout, upload defaults): [`channel/description.md`](channel/description.md),
  with the logo, banner and watermark next to it.
- **The show:** characters, arcs and every episode in [`docs/bible.md`](docs/bible.md); how to write a script in [`docs/script-format.md`](docs/script-format.md).

## Rendering on GitHub

Actions > **Render season content** > Run workflow, with `items` set to `week-1` (or `week-2` … `week-4`,
`channel-kit`, `all`, or a list such as `ep03 short12 trailer`). Each item renders in its own job (an episode
takes about 10 minutes, a Short about 3) and is attached to its release with its thumbnails.

## Requirements

Python 3.10+, `ffmpeg` on the PATH, GNU Unifont (`sudo apt-get install fonts-unifont`, or put
`unifont_jp.otf` in `fonts/`, or point `TSR_FONT` at it), and `pip install -r requirements.txt` (numpy, scipy, pillow).

## Make things

```bash
python3 scripts/render_item.py ep03 --out out          # an episode (1920x1080, 30 fps)
python3 scripts/render_item.py short12 --out out       # a Short (1080x1920, 30 fps)
python3 scripts/render_item.py trailer --out out       # the channel trailer
python3 scripts/make_thumbs.py --out out ep03          # thumbnails A and B (or: all, trailer)
python3 scripts/make_kit.py                            # logo, banner and watermark into channel/
python3 scripts/make_schedule.py                       # regenerate docs/upload-schedule.*
```

Add `--limit 60` to `render_item.py` to render only the first minute of an episode as a test. Everything is
deterministic: the same item always renders the same video, so a file can be re-rendered later and still match
its description and chapters.

## How it fits together

| | |
|---|---|
| `content/scripts/epNN.txt` | The episodes, as plain-text scripts: dialogue (`kon>mika: ...`) and stage directions (`> enter basho 4 from=edo_road`). The format is in `docs/script-format.md`. |
| `content/cast.py` | Regulars and the 28 visitors: name, kanji, look, voice, the emblem they sign on the wall. |
| `content/facts.py`, `content/words.py` | The 豆知識 fact cards (each with its sources, which go into the descriptions) and the Japanese word cards. Explanations live on these cards, never in the dialogue. |
| `content/shorts.py` | The 28 Shorts: one visitor each, cut from the episode at the `> short N start/end` marks, with a title and an on-screen hook. |
| `content/meta.py` | Titles A/B, descriptions, pinned comments, playlists, thumbnails' hook words and the calendar. |
| `engine/` | `director.py` turns a script into a timeline; `shop.py`, `cast.py`, `worlds.py` draw the 320×180 world; `ui.py` draws the cards and dialogue at 640×360; `audio.py` composes the music, ambience and sound; `render.py` puts frames and sound through ffmpeg; `thumbs.py` and `brand.py` make the thumbnails and channel art. |

### Music

Four original tracks are composed by `engine/audio.py` from code (no samples, nothing to license, nothing for
Content ID to match): *Last Bowl* (D, 76 BPM), *Paper Lantern* (A minor, 70), *Snow on the Noren* (G, 64, bells,
no drums) and *Night Market* (F, 86, shamisen). Episodes are mixed to −16 LUFS, Shorts to −15.
