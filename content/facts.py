"""Fact cards, each with the sources it was checked against (they go into the video descriptions).
Checked 5 Nov 2026."""

S = dict(
    weekender=('Tokyo Weekender: Chūka soba and the Chinese roots of ramen',
               'https://www.tokyoweekender.com/art_and_culture/history/chuka-soba-ramen-chinese-history/'),
    soranews=("SoraNews24: Japan's first ramen restaurant reopens",
              'https://soranews24.com/2020/08/13/japans-first-ever-ramen-restaurant-which-closed-44-years-ago-is-reopening-this-fall/amp/'),
    hosomichi=('Wikipedia: Oku no Hosomichi', 'https://en.wikipedia.org/wiki/Oku_no_Hosomichi'),
    bashomuseum=('Bashō Memorial Museum, Iga: chronology', 'https://www.basho-bp.jp/en/?p=10'),
    kappa=('World History Encyclopedia: Kappa', 'https://www.worldhistory.org/Kappa/'),
    kappamaki=('Sushi-pedia: kappa', 'https://www.sushi-pedia.com/en/glossary/kappa'),
    kitsune=('Wikipedia: Kitsune', 'https://en.wikipedia.org/wiki/Kitsune'),
    musashi_b=('Britannica: Miyamoto Musashi', 'https://www.britannica.com/biography/Miyamoto-Musashi-Japanese-soldier-artist'),
    musashi_d=('Discovery UK: Sasaki Kojirō and Ganryū Island',
               'https://www.discoveryuk.com/mysteries/who-was-sasaki-kojiro-and-what-happened-at-ganryu-island/'),
    tanuki=('Wikipedia: Tanuki statue', 'https://en.wikipedia.org/wiki/Tanuki_statue'),
    hokusai=("Sotheby's: 21 facts about Katsushika Hokusai", 'https://www.sothebys.com/en/articles/21-facts-about-katsushika-hokusai'),
    tsukumogami=('Uncanny Japan: haunted artifacts (tsukumogami)', 'https://uncannyjapan.com/haunted-artifacts-tsukumogami/'),
    issun=('Wikipedia: Issun-bōshi', 'https://en.wikipedia.org/wiki/Issun-b%C5%8Dshi'),
    labor=('Wikipedia: Labor Thanksgiving Day', 'https://en.wikipedia.org/wiki/Labor_Thanksgiving_Day'),
    mitsukuni=('Wikipedia: Tokugawa Mitsukuni', 'https://en.wikipedia.org/wiki/Tokugawa_Mitsukuni'),
    eel=("Hiroko's Kitchen: Hiraga Gennai and the eel", 'https://hirokoskitchen.com/blogs/all/marketing-genius-hiraga-genna-unagi-eel'),
    elekiter=('IEEE Milestone: Elekiteru, first electrostatic generator in Japan, 1776',
              'https://ethw.org/Milestones:Elekiteru:_First_Electrostatic_Generator_in_Japan,_1776'),
    gennai=('Wikipedia: Hiraga Gennai', 'https://en.wikipedia.org/wiki/Hiraga_Gennai'),
    hachiko=('nippon.com: Hachikō, the faithful dog', 'https://www.nippon.com/en/japan-glances/jg00137/hachiko-the-faithful-dog.html'),
    urashima=('Wikipedia: Urashima Tarō', 'https://en.wikipedia.org/wiki/Urashima_Tar%C5%8D'),
    bamboo=('Wikipedia: The Tale of the Bamboo Cutter', 'https://en.wikipedia.org/wiki/The_Tale_of_the_Bamboo_Cutter'),
    tsukimi=('Sudachi: Tsukimi udon', 'https://sudachirecipes.com/tsukimi-udon'),
    raijin=('Wikipedia: Raijin', 'https://en.wikipedia.org/wiki/Raijin'),
    zashiki=('yokai.jp: Zashiki-warashi', 'https://yokai.jp/en/yokai/zashiki-warashi'),
    seimei=('Wikipedia: Abe no Seimei', 'https://en.wikipedia.org/wiki/Abe_no_Seimei'),
    ino=('Wikipedia: Inō Tadataka', 'https://en.wikipedia.org/wiki/In%C5%8D_Tadataka'),
    genji=('World History Encyclopedia: Tale of Genji', 'https://www.worldhistory.org/Tale_of_Genji/'),
    sei=('Wikipedia: Sei Shōnagon', 'https://en.wikipedia.org/wiki/Sei_Sh%C5%8Dnagon'),
    pillow=('Wikipedia: The Pillow Book', 'https://en.wikipedia.org/wiki/The_Pillow_Book'),
    notes=('Al Jazeera: Japan issues first new banknotes in 20 years',
           'https://www.aljazeera.com/economy/2024/7/3/japan-issues-first-new-banknotes-in-20-years'),
    notes2=('Japan Wonder Travel: the new Japanese banknotes', 'https://jw-webmagazine.com/tips/new-japanese-banknotes'),
    shibusawa=("nippon.com: Shibusawa Eiichi, Japan's moral capitalist", 'https://nippon.com/en/views/b07202'),
    tsuda=('Wikipedia: Tsuda Umeko', 'https://en.wikipedia.org/wiki/Tsuda_Umeko'),
    kitasato=('Wikipedia: Kitasato Shibasaburō', 'https://en.wikipedia.org/wiki/Kitasato_Shibasabur%C5%8D'),
    yuki=('yokai.jp: Yuki-onna', 'https://yokai.jp/en/yokai/yuki-onna'),
    kwaidan=('Wikipedia: Kwaidan', 'https://en.wikipedia.org/wiki/Kwaidan:_Stories_and_Studies_of_Strange_Things'),
    michizane=('Wikipedia: Sugawara no Michizane', 'https://en.wikipedia.org/wiki/Sugawara_no_Michizane'),
    dazaifu=('japan-guide: Dazaifu Tenmangū', 'https://japan-guide.com/e/e4851.html'),
    baku=('Onmark Productions: Baku', 'https://www.onmarkproductions.com/html/baku.html'),
    hanzo=('All That\'s Interesting: Hattori Hanzō', 'https://allthatsinteresting.com/hattori-hanzo'),
    ronin=('Wikipedia: Forty-seven rōnin', 'https://en.wikipedia.org/wiki/Forty-seven_r%C5%8Dnin'),
    kabuki=('Wikipedia: Kabuki', 'https://en.wikipedia.org/wiki/Kabuki'),
    commontest=('Wikipedia: Common Test for University Admissions',
                'https://en.wikipedia.org/wiki/Common_Test_for_University_Admissions'),
    noren=('Japan Experience: Noren curtains', 'https://www.japan-experience.com/plan-your-trip/to-know/understanding-japan/noren'),
)


def F(title, body, *src):
    return dict(title=title, body=body, sources=[S[s] for s in src])


FACTS = {
    # Episode 1
    'noren': F('暖簾  NOREN · open for business',
               'A shop hangs its noren curtain over the door when it opens and takes it inside when it closes. '
               'It doubles as a sign: most carry the shop\'s name or crest.', 'noren'),
    'kitsune_udon': F('きつねうどん  KITSUNE UDON · fox noodles',
                      'Fried tofu (aburaage) has long been offered to foxes at Inari shrines, so in folklore foxes love it. '
                      'Noodles topped with it are called kitsune: fox.', 'kitsune'),
    'basho_journey': F('松尾芭蕉  MATSUO BASHŌ · poet, 1644–1694',
                       'In spring 1689 Bashō left Edo (now Tokyo) with his companion Sora. They walked about 2,400 km '
                       'in some 150 days: the journey of Oku no Hosomichi, The Narrow Road to the Deep North.', 'hosomichi'),
    'ramen_1910': F('ラーメン  RAMEN · a newcomer',
                    'Ramen grew out of the Chinese noodle soups of Japan\'s port towns. Rairaiken, usually called the '
                    'first ramen shop, opened in Asakusa, Tokyo, in 1910, with cooks from Yokohama\'s Chinatown.',
                    'weekender', 'soranews'),
    'old_pond': F('古池や  THE OLD POND · 1686',
                  'Furuike ya / kawazu tobikomu / mizu no oto: "an old pond / a frog jumps in / the sound of water." '
                  'Bashō wrote it in 1686. It may be the best-known haiku of all.', 'bashomuseum'),
    'kappa_dish': F('河童  KAPPA · the dish on its head',
                    'A kappa keeps water in a dish on top of its head. If the water spills, it loses its strength '
                    'until the dish is refilled. Kappa are so polite that if you bow, they bow back... and spill it.', 'kappa'),
    'kappamaki': F('かっぱ巻き  KAPPAMAKI',
                   'Kappa are famous for loving cucumbers. That\'s the usual reason given for calling a cucumber '
                   'sushi roll kappamaki, though nobody knows exactly when the name stuck.', 'kappa', 'kappamaki'),
    # Episode 2
    'musashi_duel': F('宮本武蔵  MIYAMOTO MUSASHI · 1584–1645',
                      'In 1612 Musashi fought Sasaki Kojirō on Ganryūjima, a tiny island. The famous telling says he '
                      'arrived hours late, with a wooden sword he had carved from a boat\'s oar. Accounts differ on '
                      'almost everything.', 'musashi_b', 'musashi_d'),
    'musashi_book': F('五輪書  THE BOOK OF FIVE RINGS',
                      'Late in life Musashi wrote down his strategy in The Book of Five Rings, still read today. He was '
                      'also a fine ink painter: his shrike perched in a dead tree is one of his best-known works.', 'musashi_b'),
    'tanuki_real': F('狸  TANUKI · a real animal',
                     'The tanuki is the Japanese raccoon dog, a wild member of the dog family. In folklore it\'s a '
                     'shapeshifter; in the tale Bunbuku Chagama, a tanuki turns itself into a tea kettle.', 'tanuki'),
    'tanuki_statue': F('信楽焼の狸  THE LUCKY TANUKI',
                       'Pottery tanuki from the town of Shigaraki stand outside shops and inns all over Japan for luck '
                       'and prosperity: straw hat against bad weather, a sake flask, a big round belly.', 'tanuki'),
    'kitsune_100': F('狐  KITSUNE · foxes and their tails',
                     'In Japanese folklore, the more tails a fox has, the older and wiser it is. Some tales say a fox '
                     'grows another tail only after living 100 years, and learns to take human form at about that age.',
                     'kitsune'),
    # Episode 3
    'hokusai_moves': F('葛飾北斎  KATSUSHIKA HOKUSAI · 1760–1849',
                       'Hokusai moved house about 93 times, reportedly because he hated cleaning, and used at least 30 '
                       'names. In his seventies he called himself Gakyō Rōjin: "the old man mad about painting".', 'hokusai'),
    'great_wave': F('神奈川沖浪裏  THE GREAT WAVE',
                    'The Great Wave belongs to Thirty-Six Views of Mount Fuji, a series Hokusai began around 1830, in '
                    'his seventies. He hoped his best work would come at 110. He died at 88.', 'hokusai'),
    'tsukumogami': F('付喪神  TSUKUMOGAMI · things that come alive',
                     'In folklore, an object that reaches its hundredth birthday can gain a soul. The kasa-obake is an '
                     'old paper umbrella with one big eye, a long tongue and one hairy leg. Mostly it likes to startle '
                     'people.', 'tsukumogami'),
    'issun': F('一寸法師  ISSUN-BŌSHI · the inch-high samurai',
               'In this old tale a boy one inch tall sets off for the capital in a bowl, paddling with a chopstick, '
               'with a needle for a sword. He beats an oni, and its magic mallet makes him full size.', 'issun'),
    # Episode 4
    'labor_day': F('勤労感謝の日  LABOUR THANKSGIVING DAY · 23 November',
                   'Japan\'s day for thanking workers got its modern name in 1948. It grew out of Niiname-sai, an '
                   'ancient festival of thanks for the harvest.', 'labor'),
    'mitsukuni_ramen': F('徳川光圀  TOKUGAWA MITSUKUNI · 1628–1701',
                         'The lord of Mito is often called one of the first people in Japan to eat ramen. Historians '
                         'are doubtful: noodles were served in Kyoto as early as 1488, and ramen as we know it took '
                         'shape around 1910.', 'mitsukuni', 'weekender'),
    'mito_komon': F('水戸黄門  MITO KŌMON',
                    'On television, Mitsukuni roams Japan in disguise, punishing crooked officials; the series Mito '
                    'Kōmon ran from 1969 to 2011. The real lord gathered scholars to write a huge history of Japan, '
                    'the Dai Nihonshi.', 'mitsukuni'),
    'gennai_eel': F('平賀源内  HIRAGA GENNAI · about 1729–1780',
                    'Legend says an eel shop asked Gennai how to sell eel in summer, and he suggested a sign: today '
                    'is the Day of the Ox. Japan still eats eel on that day. Whether he really did, nobody knows.',
                    'eel', 'gennai'),
    'elekiter': F('エレキテル  THE ELEKITER · 1776',
                  'Gennai spent years rebuilding a broken Dutch electrostatic generator and showed it off in 1776: the '
                  'first in Japan. People came to see the sparks, and it was used as a medical device.', 'elekiter'),
    # Episode 5
    'hachiko': F('ハチ公  HACHIKŌ · 1923–1935',
                 'Every evening Hachikō met his owner, Professor Ueno Hidesaburō, at Shibuya Station. Ueno died in May '
                 '1925. Hachikō kept coming back to the station, morning and evening, for almost ten years.', 'hachiko'),
    'hachiko_statue': F('ハチ公像  THE STATUE',
                        'A bronze statue of Hachikō was put up at Shibuya Station in 1934, while he was still alive. '
                        'It was melted down during the war and rebuilt about three years after it ended.', 'hachiko'),
    'urashima': F('浦島太郎  URASHIMA TARŌ',
                  'A fisherman rescues a turtle and visits the Dragon Palace under the sea. In the version children '
                  'learn today he stays three days; back home, about 300 years have passed. Older versions say 700.',
                  'urashima'),
    'urashima_box': F('玉手箱  THE BOX',
                      'The princess gives him a box and warns him never to open it. He opens it, white smoke pours out, '
                      'and he is suddenly old. An early form of the tale is in the Nihon Shoki, under the year 478.',
                      'urashima'),
    # Episode 6
    'kaguya': F('かぐや姫  THE TALE OF THE BAMBOO CUTTER',
                'Written in the 9th or 10th century, the oldest surviving Japanese monogatari. An old man finds a tiny '
                'girl in a shining bamboo stalk. She sets her five suitors impossible tasks, then returns to the Moon.',
                'bamboo'),
    'fuji_elixir': F('富士山  MOUNT FUJI',
                     'Before she leaves, Kaguya-hime sends the Emperor an elixir of immortality. He has it burned on the '
                     'highest mountain. Legend links the name Fuji to "immortal", and says the smoke still rises.', 'bamboo'),
    'raijin': F('雷神  RAIJIN · god of thunder',
                'Raijin beats a ring of taiko drums to make thunder. Some Japanese parents tell their children to hide '
                'their belly buttons in a thunderstorm, or Raijin will take them.', 'raijin'),
    'zashiki': F('座敷童子  ZASHIKI-WARASHI',
                 'A child spirit from northern Japan. In Tales of Tōno (1910), a house where one lives enjoys good '
                 'fortune, and when it leaves, the family\'s luck can fail. Not everyone in the house can see it.',
                 'zashiki'),
    # Episode 7
    'seimei': F('安倍晴明  ABE NO SEIMEI · 921–1005',
                'The most famous onmyōji, a court diviner and astrologer of the Heian era. Legend says his mother, '
                'Kuzunoha, was a fox. A shrine was built at his home in Kyoto in 1007; its symbol is his five-pointed star.',
                'seimei'),
    'ino': F('伊能忠敬  INŌ TADATAKA · 1745–1818',
             'A sake brewer and rice merchant who retired at 49 and began surveying Japan at about 55. He walked some '
             '35,000 km in 17 years, mostly counting his steps. His team finished his map in 1821, after his death.',
             'ino'),
    # Episode 8
    'genji': F('源氏物語  THE TALE OF GENJI',
               'Murasaki Shikibu wrote it at the Heian court in the early 1000s, while serving Empress Shōshi. Its 54 '
               'chapters follow the life and loves of Prince Genji. It is often called the world\'s first novel.', 'genji'),
    'pillow_book': F('枕草子  THE PILLOW BOOK',
                     'Sei Shōnagon served Empress Teishi from about 993. Her Pillow Book is full of observations, '
                     'gossip and lists, such as "Hateful Things". It was probably finished between 1001 and 1010.',
                     'sei', 'pillow'),
    'rivals': F('ライバル?  RIVALS?',
                'Murasaki served Empress Shōshi; Sei had served her rival, Empress Teishi. In her diary Murasaki wrote '
                'scathingly about Sei, while granting her talent.', 'sei'),
    # Episode 9
    'new_notes': F('新紙幣  NEW BANKNOTES · 3 July 2024',
                   'Japan\'s first new banknotes in 20 years have 3D hologram portraits that turn as you tilt them: '
                   'Shibusawa Eiichi on the 10,000 yen, Tsuda Umeko on the 5,000, Kitasato Shibasaburō on the 1,000.',
                   'notes', 'notes2'),
    'shibusawa': F('渋沢栄一  SHIBUSAWA EIICHI · 1840–1931',
                   'Called the father of Japanese capitalism. He helped found and run roughly 500 companies, among them '
                   'the First National Bank, and worked with about 600 charities and social causes.', 'shibusawa'),
    'tsuda': F('津田梅子  TSUDA UMEKO · 1864–1929',
               'At six she sailed to America in 1871, the youngest member of the Iwakura Mission, and studied there '
               'until she was 18. In 1900 she founded a school for women in Tokyo: today\'s Tsuda University.', 'tsuda'),
    'kitasato': F('北里柴三郎  KITASATO SHIBASABURŌ · 1853–1931',
                  'In 1889 he was the first to grow the tetanus bacillus in pure culture; in 1890, with Emil von Behring, '
                  'he developed serum therapy. In 1894 in Hong Kong he identified the plague bacterium; Alexandre '
                  'Yersin found it days later, and the credit is still debated.', 'kitasato'),
    # Episode 10
    'yuki': F('雪女  YUKI-ONNA · the snow woman',
              'A woman all in white who appears on snowy nights. Lafcadio Hearn\'s book Kwaidan (1904) made her famous '
              'abroad; a tale from 1685 already describes skin "so white it seems transparent".', 'yuki', 'kwaidan'),
    'michizane': F('菅原道真  SUGAWARA NO MICHIZANE · 845–903',
                   'A great scholar, exiled to Dazaifu in 901. After his death he was honoured as Tenjin and became '
                   'the god of learning. Students still pray at his shrines before entrance exams.', 'michizane', 'dazaifu'),
    'tobiume': F('飛梅  THE FLYING PLUM',
                 'Michizane loved plum trees. Before leaving Kyoto he wrote a poem to his own: when the east wind blows, '
                 'send me your scent. Legend says the tree flew after him to Dazaifu.', 'michizane', 'dazaifu'),
    'common_test': F('共通テスト  THE COMMON TEST',
                     'Japan\'s national university entrance exam is held over a weekend every January. For many '
                     'students, autumn and winter are cram season.', 'commontest'),
    # Episode 11
    'baku': F('獏  BAKU · the dream eater',
              'It has an elephant\'s trunk, a rhinoceros\'s eyes, an ox\'s tail and a tiger\'s paws, and it eats bad '
              'dreams. People put pictures of the baku under their pillows, above all for the first dream of the New Year.',
              'baku'),
    'hanzo': F('服部半蔵  HATTORI HANZŌ · 1542–1596',
               'Pop culture made him the ultimate ninja. He was a samurai commander of Tokugawa Ieyasu, nicknamed '
               '"Demon Hanzō". Hanzōmon gate at the Imperial Palace and Tokyo\'s Hanzōmon subway line are named after him.',
               'hanzo'),
    # Episode 12
    'ronin': F('四十七士  THE 47 RŌNIN',
               'In 1703 (31 January by today\'s calendar) 47 masterless samurai led by Ōishi Kuranosuke avenged their '
               'lord. To fool spies, Ōishi had pretended to live a careless life. Japan remembers them every 14 December.',
               'ronin'),
    'chushingura': F('忠臣蔵  CHŪSHINGURA',
                     'Their story became Chūshingura, retold on stage and screen ever since. They are buried together at '
                     'Sengaku-ji temple in Tokyo, which holds a festival for them on 14 December.', 'ronin'),
    'okuni': F('出雲阿国  IZUMO NO OKUNI · kabuki begins',
               'In 1603 Okuni and her troupe began dancing a bold new kind of show on the dry riverbed of Kyoto\'s Kamo '
               'River. It became kabuki. In 1629 women were banned from the kabuki stage; it has been all-male since.',
               'kabuki'),
}
