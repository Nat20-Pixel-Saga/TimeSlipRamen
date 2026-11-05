# Writing an episode

An episode is a plain-text file, `content/scripts/epNN.txt`, read by `engine/director.py`. Three kinds of line:

```text
@title Two Hundred Years Too Early        header: starts with @
> enter basho 4 from=edo_road cap="Edo · 1689"   command: starts with >
kon>mika: What did you tell her? [w:moshi]        dialogue: who: text, or who>target: text
```

Commands and lines run one after another. A trailing `&` runs a command alongside the next ones (`> cook 3 &`).
Every character has their own queue, so nobody teleports when two things overlap. Lines starting with `#`
are comments.

## The house rule

Nobody explains anything in dialogue. A Japanese word gets a word card (`[w:itadakimasu]` on the line, or
`> word itadakimasu`); a fact gets a 豆知識 card (`> card hachiko_statue`). Cards sit on top of the picture and
their sources go into the description automatically.

## Headers

| Header | |
|---|---|
| `@number 3`, `@title …` | Shown on the title card. `@subtitle …` replaces the "Episode N" line. |
| `@weather rain` | `rain`, `snow`, `storm` or `clear` at the start (change it later with `> weather`). |
| `@music snow_noren paper_lantern` | Tracks in order, looped to the episode's length: `last_bowl`, `paper_lantern`, `snow_noren`, `night_market`. |
| `@present gen:6 kon:2 mika:1` | Who is already sitting, on which stool (1–6, left to right). |
| `@teaser label 10` | Cold open: the 10 seconds after `> mark label` are played before the title. |
| `@kasa`, `@zashiki` | Grandpa's umbrella asleep in the stand; the house spirit by the window. |
| `@tails 2` | Kon's tail count. |
| `@endhead …` | The heading of the end card (default "NEXT TIME AT TIMESLIP RAMEN"). |

## Dialogue

`who: text` or `who>target: text` (the speaker turns to face the target). Inline tags: `[w:wordid]` shows a
word card with the line, `[slow]` types slowly, `[+0.6]` adds a pause after the line.

## Commands

**Timing and structure**

| | |
|---|---|
| `wait 2` | Pause. |
| `title [5.5]` | Show the title card. |
| `chapter Name` | A YouTube chapter at this moment (the first one is always "Cold open" at 0:00). |
| `mark label` / `label name` | A named moment (for `@teaser`). |
| `short N start` … `short N end` | The windows that make Short N. A Short may use several windows. |
| `establish view "caption" [2.8]` | Full-screen shot of another place and time. |
| `end Line one. \| Line two.` | The end card; `\|` breaks lines. |
| `cam x` | (Shorts) hint where to look; the camera otherwise follows whoever talks. |

**Visitors**

| | |
|---|---|
| `enter who 4 [from=view] [cap="…"] [speed=40] [rattle=0]` | Walk in through the door to stool 4 (or `x:120`, `floor:200`, `counter:150`). With `cap`, an establishing shot of `from` first. |
| `leave who [to=view]` | Walk out (the door shows `view`). |
| `appear who 4` / `vanish who` | Pop in or out with a puff of smoke. |
| `move who 5`, `stand who`, `sitdown who 4`, `dance who 80 9` | Moving around. |
| `look who left 3` | Turn the head for a few seconds. |
| `sign who` | Haru brings a shikishi board; the visitor signs; it goes on the wall. |
| `card who` | The visitor's name plate (or a fact card id). |
| `transform who human_fail 4` | Kon's disguises (`human_fail`, `heian_fail`, `gen_fail`, `human`), the tanuki's `kettle`, `none`. |
| `set who key value [dur]` | Tweak a drawing value for a while: `hdy` (head bob), `tails`, `paper`, `reach`, `wobble` … |
| `wake who`, `sleep who` | The umbrella (or anyone) opens or closes its eye. |

**Haru and the food**

| | |
|---|---|
| `cook 3` | Haru stirs the pot. `haru 5` moves her (`haru x pose`). `bow who` |
| `serve who dish` | Cook, carry and serve: `shoyu`, `miso`, `kitsune`, `tsukimi`, `cold`, `frozen`. |
| `eat who 6 2` | Eat for 6 s with 2 slurps. `slurp who`, `finish who [empty]`, `clear who`, `spill who`, `refill who`. |

**The room**

| | |
|---|---|
| `prop name [seat=1 dx=-12 dur=…]` / `unprop name` | Things on the counter: `notebook`, `cards`, `box`, `elekiter`, `oar`, `plum`, `paper`, `cup`, `stack`, `party`, `bubble`, `smoke`, `needle`, `leaf`. |
| `cho eye=wide look=-2,1` | Chō the lantern (`eye=open/wide/closed/wink`, `look=dx,dy`, `talk=1`). |
| `weather snow`, `flash`, `light x y r col k dur`, `unlight` | Weather, lightning, a coloured light. |
| `sfx name`, `maneki 3`, `staff who`, `hatoff who`, `boards a b` | Sound effects, the lucky cat waves, props in hand, hats, extra boards. |

Views for `from=`, `to=` and `establish`: `street`, `edo_road`, `river`, `sea`, `coast`, `forest`, `edo_town`,
`edo_castle`, `bamboo`, `storm`, `heian`, `meiji`, `shibuya`, `snow_mtn`, `plum`, `dream`, `shrine`, `kyoto_river`.
