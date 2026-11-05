"""The 28 Shorts of Season 1: one visitor each, cut from that visitor's episode (cold open,
talking from the first frame, no fades so it loops).  Windows are marked in the scripts with
`> short N start/end`; a Short may use several windows from the same episode.

Each entry: n, episode, visitor, YouTube title, on-screen hook (first 2.6 s), extra options.
Options: music=<track> (default: the episode's first track), cam=<x> (default: the visitor's
seat at the start of the window), tags=[...] (extra hashtags for the description).
"""

SHORTS = [
    (1, 1, 'basho', "A haiku poet from 1689 walks into a ramen shop", "200 years too early", {}),
    (2, 1, 'kappa', "Never bow to a kappa", "Never bow to a kappa", {}),
    (3, 2, 'musashi', "Miyamoto Musashi is always late. On purpose.", "Late. On purpose.", {}),
    (4, 2, 'tanuki', "The tanuki who turned into a tea kettle", "Totally normal human", {'music': 'night_market'}),
    (5, 3, 'hokusai', "Hokusai moved 93 times. His secret: never clean", "93 house moves", {}),
    (6, 3, 'kasa', "Grandpa's umbrella just turned 100", "The umbrella woke up", {'cam': 70}),
    (7, 3, 'issun', "A table for one... inch?", "Table for one inch", {}),
    (8, 4, 'mitsukuni', "Was Mito Kōmon Japan's first ramen eater?", "Japan's first ramen?", {}),
    (9, 4, 'gennai', "The man who sold eel with a slogan", "Business slow?", {'music': 'night_market'}),
    (10, 5, 'hachiko', "A taxi driver meets Hachikō", "Who's a good boy?", {'music': 'paper_lantern'}),
    (11, 5, 'urashima', "Don't open the box", "DON'T open the box", {}),
    (12, 6, 'kaguya', "The Moon Princess ordered the impossible", "An impossible order", {}),
    (13, 6, 'raijin', "Cover your belly button!", "Cover your belly button", {'music': 'paper_lantern'}),
    (14, 6, 'zashiki', "Only some people can see her", "Who can see her?", {'cam': 96}),
    (15, 7, 'seimei', "A fox asks Abe no Seimei how to turn human", "His mother was a fox", {}),
    (16, 7, 'ino', "He started at 55 and walked 35,000 km", "Started at 55", {}),
    (17, 8, 'murasaki', "Murasaki Shikibu vs Sei Shōnagon", "Rivals since 1000 AD", {}),
    (18, 8, 'sei', "Two famous writers, opposite essay advice", "Need essay advice?", {}),
    (19, 9, 'shibusawa', "He's on the 10,000 yen note (and didn't know)", "Is that... me?", {}),
    (20, 9, 'tsuda', "She crossed the ocean to study. Age six.", "Is there a 5,000?", {}),
    (21, 9, 'kitasato', "The 1,000-yen doctor inspected my kitchen", "And the thousand?", {}),
    (22, 10, 'yuki', "It was snowing. She asked for something colder", "Something cold, please", {}),
    (23, 10, 'michizane', "The god students pray to before exams", "The god of exams", {'music': 'paper_lantern'}),
    (24, 11, 'baku', "A baku ate her exam nightmare. Crunchy.", "It eats nightmares", {}),
    (25, 11, 'hanzo', "Hattori Hanzō is NOT a ninja", "NOT a ninja", {'music': 'last_bowl'}),
    (26, 12, 'oishi', "A samurai orders 47 bowls of ramen to go", "47 bowls. To go.", {}),
    (27, 12, 'grandma', "The fox turned 100 tonight", "Kon turns 100", {'music': 'last_bowl'}),
    (28, 12, 'okuni', "Kabuki was started by a woman", "She started kabuki", {}),
]


def by_number(n):
    for s in SHORTS:
        if s[0] == n:
            d = dict(n=s[0], ep=s[1], who=s[2], title=s[3], hook=s[4])
            d.update(s[5])
            return d
    raise KeyError(n)


def all_shorts():
    return [by_number(s[0]) for s in SHORTS]
