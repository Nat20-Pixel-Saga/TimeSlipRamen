"""Season 1 · Rainy Nights: titles (A/B), descriptions, pinned comments, playlists and the
upload schedule.  Everything YouTube needs is generated from here by scripts/make_schedule.py.

A/B: YouTube Studio > Test & compare.  A = the story title and a close-up thumbnail of the
visitor with hook words; B = a cozy, searchable title and a no-words thumbnail of the shop.
"""
import datetime as dt

CHANNEL = 'Timeslip Ramen'
HANDLE = '@TimeslipRamen'
TZ = 'Europe/Berlin'           # CET in Nov/Dec (UTC+1)
EP_TIME, SHORT_TIME = '17:00', '19:00'
SEASON = 'Season 1 · Rainy Nights'
START = dt.date(2026, 11, 16)  # Monday

TRAILER = dict(id='trailer', date='2026-11-14', time='17:00',
               title='Timeslip Ramen: a pixel ramen shop where history walks in out of the rain',
               title_b='A cozy pixel ramen shop open to every century 🍜 (channel trailer)')

# n: (title A, title B, hook for the description, pinned comment)
EPISODES_META = {
    1: ("Bashō walks into a ramen shop 200 years too early",
        "Rainy night at a cozy pixel ramen shop 🍜 lofi, rain & Japanese history",
        "Japan's most famous poet walks in from the year 1689, a kappa wants cucumbers, and you meet the "
        "regulars: Haru the cook, Kon the fox, Mika and Gen-san.",
        "Bashō signed the wall tonight. Who would YOU want to see walk through that door?"),
    2: ("The samurai who was late on purpose",
        "Closing time at a cozy pixel ramen shop 🍜 rain, a samurai & a tanuki",
        "Miyamoto Musashi turns up five minutes before closing, exactly as planned. Then a tanuki in a very "
        "convincing disguise has a score to settle with Kon.",
        "Kon is 99. What do you think happens when a fox turns 100?"),
    3: ("Hokusai moved house 93 times. Then he came for ramen",
        "Cozy pixel ramen shop on a rainy night 🌊 Hokusai, yōkai & lofi",
        "The painter of The Great Wave needs a place to sit (he has moved 93 times). Grandpa's old umbrella turns "
        "one hundred and wakes up. And a customer rows in on a soup bowl.",
        "Grandpa's umbrella needs a name. What should Haru call it?"),
    4: ("Who ate Japan's first ramen?",
        "Rainy holiday night at a cozy pixel ramen shop 🍜 Mito Kōmon & lofi",
        "Labour Thanksgiving Day. Tokugawa Mitsukuni claims the first bowl of ramen in Japan, Gen-san meets his TV "
        "hero, and Hiraga Gennai has a slogan (and a spark) to save a slow Monday.",
        "Gennai wrote Japan's most famous food slogan. Write one for Haru's shop below."),
    5: ("Hachikō came in from the rain",
        "A dog, the rain and a warm bowl 🐕 cozy pixel ramen shop",
        "A very good dog waits by the door, and Gen-san softens. Then Urashima Tarō has been away \"three days\" "
        "and is carrying a box nobody should open.",
        "Would you open Urashima's box? Be honest."),
    6: ("The thunder god wants your belly button",
        "Thunderstorm at a cozy pixel ramen shop ⛈️ Japanese folklore & lofi",
        "Kaguya-hime orders the impossible. Raijin storms in and Gen-san finally stops calling it cosplay. And a "
        "little girl by the window has been there all along.",
        "A zashiki-warashi brings luck to the house she lives in. Whose house would you send her to?"),
    7: ("Japan's greatest wizard. His mother was a fox.",
        "Rainy night ramen with a Heian wizard 🦊 cozy pixel lofi",
        "Abe no Seimei gives Kon advice about being half-fox. Inō Tadataka measures the shop in footsteps, and "
        "Gen-san decides he isn't too old to start something.",
        "Inō started his life's work at 55. What would you start tomorrow?"),
    8: ("Japan's oldest rivalry, two stools apart",
        "Two writers at a cozy pixel ramen counter 📜 rain & lofi",
        "Murasaki Shikibu and Sei Shōnagon end up two stools apart, a thousand years after they stopped talking. "
        "Mika needs essay advice; Kon tries a court disguise.",
        "Team Murasaki (one long story) or Team Sei (lists)? Make your case."),
    9: ("The people on your money came in for ramen",
        "Rainy Meiji-era night at a cozy pixel ramen shop 💴 lofi",
        "Shibusawa Eiichi, Tsuda Umeko and Kitasato Shibasaburō walk in together, and Gen-san pays with their faces. "
        "Meanwhile, the regulars plan something for Kon. Quietly.",
        "Who's on YOUR country's banknotes? Tell us below and we might invite them in."),
    10: ("The Snow Woman wants it colder",
         "First snow at a cozy pixel ramen shop ❄️ yōkai & lofi",
         "The first snow of the season brings Yuki-onna, who finds everything a little too warm, and Sugawara no "
         "Michizane, the god students pray to before exams.",
         "Good luck to everyone with exams this winter. What are you studying for?"),
    11: ("It ate her nightmare",
         "Snowy night ramen and a dream eater 🌙 cozy pixel lofi",
         "Mika falls asleep over her notes and a baku comes in to eat the nightmare. Then Hattori Hanzō insists, "
         "firmly, that he is not a ninja, and hides something for Friday.",
         "What nightmare would you feed the baku?"),
    12: ("Forty-seven bowls to go (season finale)",
         "Snowy birthday party at a cozy pixel ramen shop 🎉 lofi",
         "Ōishi Kuranosuke orders forty-seven bowls to go. Kon turns one hundred and someone very special comes to "
         "the party. Okuni dances, Mika gets her result, and the lantern says something.",
         "Season 1 is done. Who should walk in during Season 2?"),
}

# a short line about each visitor for the description ("Tonight at the counter")
VISITOR_LINES = {
    'basho': "Matsuo Bashō (1644–1694), haiku poet, on the road to the Deep North",
    'kappa': "a kappa, river yōkai with a dish of water on its head",
    'musashi': "Miyamoto Musashi (c. 1584–1645), swordsman and author of The Book of Five Rings",
    'tanuki': "a tanuki, shapeshifting raccoon dog of folklore",
    'hokusai': "Katsushika Hokusai (1760–1849), painter of The Great Wave",
    'kasa': "a kasa-obake, an umbrella that turned one hundred",
    'issun': "Issun-bōshi, the one-inch boy of the fairy tale",
    'mitsukuni': "Tokugawa Mitsukuni (1628–1701), lord of Mito, \"Mito Kōmon\"",
    'gennai': "Hiraga Gennai (1728–1780), inventor, writer and slogan-maker",
    'hachiko': "Hachikō (1923–1935), the dog who waited at Shibuya",
    'urashima': "Urashima Tarō, the fisherman of the old tale",
    'kaguya': "Kaguya-hime, the princess from the Moon",
    'raijin': "Raijin, god of thunder",
    'zashiki': "a zashiki-warashi, the child spirit of a lucky house",
    'seimei': "Abe no Seimei (921–1005), court diviner of Heian Kyoto",
    'ino': "Inō Tadataka (1745–1818), who mapped Japan on foot",
    'murasaki': "Murasaki Shikibu, author of The Tale of Genji",
    'sei': "Sei Shōnagon, author of The Pillow Book",
    'shibusawa': "Shibusawa Eiichi (1840–1931), on the new 10,000-yen note",
    'tsuda': "Tsuda Umeko (1864–1929), on the new 5,000-yen note",
    'kitasato': "Kitasato Shibasaburō (1853–1931), on the new 1,000-yen note",
    'yuki': "Yuki-onna, the snow woman",
    'michizane': "Sugawara no Michizane (845–903), scholar, later Tenjin, god of learning",
    'baku': "a baku, the dream eater",
    'hanzo': "Hattori Hanzō (1542–1596), samurai commander (not a ninja)",
    'oishi': "Ōishi Kuranosuke (1659–1703), leader of the Forty-Seven Rōnin",
    'grandma': "Kon's grandmother, a nine-tailed fox",
    'okuni': "Izumo no Okuni, who began kabuki around 1603",
}

HASHTAGS = '#TimeslipRamen #pixelart #japanesehistory #cozy #lofi'
SHORT_TAGS = '#shorts #TimeslipRamen #pixelart #japan'

PLAYLISTS = [
    dict(name='Season 1 · Rainy Nights (full episodes)', items='ep01-ep12, in order',
         description='Twelve rainy (and two snowy) nights at a ramen shop whose door opens onto any century.'),
    dict(name='Shorts · one visitor a day', items='short01-short28, in order',
         description='One visitor from Japanese history or folklore every day, straight from the counter.'),
    dict(name='Folklore & yōkai', items='ep01, ep02, ep03, ep05, ep06, ep10, ep11',
         description='Kappa, tanuki, a hundred-year-old umbrella, the thunder god, the snow woman and a dream eater.'),
    dict(name='People from history', items='ep01, ep02, ep03, ep04, ep05, ep07, ep08, ep09, ep10, ep11, ep12',
         description='Poets, painters, samurai, scientists and writers, each with sourced facts on screen.'),
]


def episode_dates():
    """Mon/Wed/Fri from START: 12 episodes."""
    out, d = [], START
    while len(out) < 12:
        if d.weekday() in (0, 2, 4):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def short_dates():
    """One Short a day from START: Short n on day n (28 days, 16 Nov - 13 Dec)."""
    return [START + dt.timedelta(days=i) for i in range(28)]

# Thumbnail A: who stands in the doorway, and two lines of hook words (B has no words)
THUMBS = {
    1: ('basho', ('200 YEARS', 'TOO EARLY')),
    2: ('musashi', ('LATE', 'ON PURPOSE')),
    3: ('hokusai', ('MOVED', '93 TIMES')),
    4: ('mitsukuni', ("JAPAN'S", 'FIRST RAMEN?')),
    5: ('hachiko', ("HE'S STILL", 'WAITING')),
    6: ('raijin', ('NOT', 'COSPLAY')),
    7: ('seimei', ('HIS MOTHER', 'WAS A FOX')),
    8: ('murasaki', ('1,000-YEAR', 'RIVALS')),
    9: ('shibusawa', ('IS THAT', 'ME?')),
    10: ('yuki', ('SHE WANTS', 'IT COLDER')),
    11: ('baku', ('IT EATS', 'NIGHTMARES')),
    12: ('oishi', ('47 BOWLS', 'TO GO')),
}
