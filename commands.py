# coding: utf-8
import re
import os
import random
import config
import aiohttp
import json
import motor.motor_asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aiosqlite
import sosach
import urbandict
import wolframalpha
import wikipedia
from yandex_translate import YandexTranslate
import gtts
from cowpy import cow
from game import Game
from livechanapi import post

commands = []

regioncodes = json.load(open('regioncodes.json', encoding='utf-8'))
mongo_client = motor.motor_asyncio.AsyncIOMotorClient()
khposts = mongo_client.kh_db.posts
chat_db = mongo_client.livechan_db.chat_dbs
wolfram = wolframalpha.Client(config.wolframAPI)
game = Game()
tarot_cards = json.load(open('tarot.json'))
error_cache = json.load(open('errors.json')) if os.path.exists('errors.json') else {}
hellos = {'Arabic': 'Marhaba',
          'DE-02': 'Grüß Gott',
          'AU': 'Grüß Gott',
          'CN': 'Nǐ hǎo',
          'DK': 'God dag',
          'FI': 'hyvää päivää',
          'FR': 'Bonjour',
          'DE': 'Guten tag',
          'IL': 'Shalom',
          'HU': 'Jo napot',
          'JP': 'Konnichiwa',
          'KR': 'Ahn nyong ha se yo',
          'Persian': 'Salam',
          'PL': 'Cześć',
          'ES': 'Hola',
          'RU': 'Privet'}


def command(regex=None, pass_data=False, to_convo=None, from_convo=None, command_name='__default__', post_avatar=True,
            hidden=False, ignore_case=False):
    def decorator(func):
        reg = re.compile(r'\.{}$|\.{}\s(.+)'.format(func.__name__, func.__name__),
                         flags=re.IGNORECASE if ignore_case else 0)
        if regex:
            reg = re.compile(regex)

        async def callback(data):
            match = reg.match(data['body'])
            convo = data['convo']
            if match and (convo == from_convo or (from_convo is None)):
                query = (match.group(1) or '').strip()
                try:
                    if pass_data:
                        res = await func(data, query)
                    else:
                        res = await func(query)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    lang = data.get('country', 'US').split('-')[0].lower()
                    if lang == 'us':
                        lang = 'en'
                    if lang not in error_cache:
                        translator = YandexTranslate(config.yandex_translate_key)
                        error_cache[lang] = translator.translate(config.error_message, 'en-{}'.format(lang))['text'][0]
                        with open('errors.json', 'w') as f:
                            json.dump(error_cache, f)
                    res = error_cache[lang]
                if not res:
                    return
                elif type(res) in (str,):
                    body, file = res, None
                else:
                    body, file = res
                if not file and post_avatar:
                    file = os.path.join(config.avatar_folder, random.choice(os.listdir(config.avatar_folder)))
                body = u'>>{}\n{}'.format(data['count'], body)
                await post(body, config.bot_name, to_convo if to_convo else data['convo'], config.bot_trip, file)
                return match

        callback.__doc__ = func.__doc__
        callback.hidden = hidden
        if command_name == '__default__':
            callback.__name__ = func.__name__
        elif command_name:
            callback.__name__ = command_name
        commands.append(callback)
        return func

    if callable(regex):
        func = regex
        regex = None
        return decorator(func)
    return decorator


@command
async def help(arg):
    'Commands help'
    # out_message = 'Commands are: {}'.format(' '.join(cmd.__name__ for cmd in commands))
    out_message = 'Commands are:\n'
    out_message += '\n'.join(['{} - {}'.format(cmd.__name__, cmd.__doc__) for cmd in commands if not cmd.hidden])
    return out_message


@command(to_convo='reddit')
async def reddit(subreddit=None):
    'Get picture from reddit'
    async with aiohttp.ClientSession() as session:
        if not subreddit:
            subreddit = 'pics'
        async with session.get('https://www.reddit.com/r/%s/top.json?sort=top&t=week&limit=100' % subreddit,
                               headers={'User-Agent': '/r/your_user_name'}) as s:
            res = await s.json()
            res = res['data']['children']
        if not res:
            return 'no such subreddit'
        post = random.choice(res)['data']
        text = post['title']
        if 'i.imgur.com' not in post['url'] and 'imgur.com' in post['url']:
            async with session.get(post['url']) as s:
                data = await s.text()
            response = re.findall(r'(http://i.imgur.com/[\w\.]+)', data)
            if response:
                post['url'] = response[0]
        if "i.imgur.com" in post['url'] or post['url'].lower().endswith('.jpg') or post['url'].lower().endswith(
                '.png') or 'i.reddituploads.com' in post['url']:
            async with session.get(post['url']) as s:
                data = await s.read()
            img = 'tmp/reddit%s' % os.path.splitext(post['url'])[1]
            if not os.path.splitext(post['url'])[1]:
                img = 'tmp/reddit.jpg'
            with open(img, 'wb') as out_file:
                out_file.write(data)
            return text, img
        elif 'imgur.com' in post['url']:
            async with session.get(post['url']) as s:
                data = await s.text()
            bs = BeautifulSoup(data)
            post['url'] = urljoin('https://imgur.com', bs.find('img')['src'])
            async with session.get(post['url']) as s:
                data = await s.read()
            img = 'tmp/reddit%s' % os.path.splitext(post['url'])[1]
            if not os.path.splitext(post['url'])[1]:
                img = 'tmp/reddit.jpg'
            with open(img, 'wb') as out_file:
                out_file.write(data)
            return text, img
        if post['url']:
            text += "\n%s" % post['url']
        if post.get('selftext'):
            text += "\n%s" % post['selftext']
        return text


@command
async def bible(arg):
    'Bible quote'
    # random.choice(json.load(open('lenin.json')))
    if not arg:
        with open('kjv.json') as bible:
               return random.choice(json.load(bible))


#   async with aiohttp.ClientSession() as sess:
#       async with sess.get('http://labs.bible.org/api/?passage=random') as s:
#           res = await s.text()
#       res = res.replace('<', '[').replace('>', ']')
#       return res


@command
async def quran(arg):
    'Quran quote'
    async with aiohttp.ClientSession() as sess:
        async with sess.get('http://quranapi.azurewebsites.net/api/verse/?lang=en') as s:
            res = await s.json()
            return res['Text']


@command
async def jft(arg):
    'Just for today.'
    async with aiohttp.ClientSession() as sess:
        async with sess.get('https://jftna.org/jft/') as s:
            t = await s.text()
            bs = BeautifulSoup(t)
            return '\n'.join([r.text for r in bs('td')][3:-1])


@command
async def lenin(arg):
    'Communist quotes'
    return random.choice(json.load(open('lenin.json')))


@command(regex=r'\.kc((\-strict){0,1}\s[\s\S]+)', to_convo='kc quotes')
async def kc(needle=''):
    'kc archive'
    strict = False
    if needle.startswith('-strict'):
        strict = True
        needle = needle.split(None, 1)[1]
    if needle == 'count':
        c = await khposts.count()
        res = '%s' % c
    else:
        if needle:
            # if needle[-1] == "*":
            #     needle = res.escape(needle[:-1])  ## BUG?
            # else:
            if strict:
                needle = '(?:^|\W){}(?:$|\W)'.format(
                    re.escape(needle))  # avoid selecting partial words (ex. .kc supple does not match "supplement")
            else:
                needle = re.escape(
                    needle)  # + r'[^a-zA-Z]*' #should avoid selecting partial words (ex. .kc supple does not match "supplement")
            needle = re.compile(needle, re.IGNORECASE)
            cursor = khposts.aggregate([{'$match': {'com': {'$regex': needle}}}, {'$sample': {'size': 1}}])
            text = await cursor.to_list(length=1)
            text = text[0]
        else:
            cursor = khposts.aggregate([{'$sample': {'size': 1}}])
            text = await cursor.to_list(length=1)
            text = text[0]
        res = '\n'.join(line for line in text['com'].splitlines() if not line.startswith('>>'))
        if not res.strip():
            return kc(needle)
        date = datetime.fromtimestamp(text['time']).strftime('%Y-%m-%d %H:%M')
        res = "%s\n(%s %s)" % (res, text.get('country_name', 'proxy'), date)
    return res


@command
async def stats(days):
    'Shitposters'
    async with aiosqlite.connect('lb.sqlite') as conn:
        if days.isdigit():
            days = int(days)
        else:
            days = None
        if not days:
            cur = await conn.execute('SELECT name,country,count(id) as c FROM posts GROUP BY ident ORDER BY c DESC LIMIT 20')
        else:
            cur = await conn.execute(
                'SELECT name,country,count(id) as c FROM posts WHERE date>? GROUP BY ident ORDER BY c DESC LIMIT 20',
                (datetime.now() - timedelta(days=days),))
        data = await cur.fetchall()
        return '\n'.join('%s | %s | %s' % row for row in data)


@command
async def countries(arg):
    'Shitposters by country'
    async with aiosqlite.connect('lb.sqlite') as conn:
        cur = await conn.execute(
            'SELECT country_name,count(id) as c FROM posts WHERE country_name!="" GROUP BY country_name ORDER BY c DESC LIMIT 20')
        data = await cur.fetchall()
        return '\n'.join('%s|%s' % row for row in data)


@command
async def regions(arg):
    'Shitposters by region'
    async with aiosqlite.connect('lb.sqlite') as conn:
        cur = conn.execute(
            'SELECT country,count(id) as c FROM posts WHERE country!="" GROUP BY country ORDER BY c DESC LIMIT 20')
        return '\n'.join('%s|%s' % row for row in cur.fetchall())


@command
async def gondola(board):
    'Gondolas'
    async with aiohttp.ClientSession() as sess:
        async with sess.get('https://gondola.stravers.net/random') as s:
            res = await s.text()
            url = res.split('source src="')[1].split('"')[0]
        img = "tmp/%s" % url.split('/')[-1]
        if not os.path.exists(img):
            async with sess.get('https://gondola.stravers.net%s' % url) as s:
                data = await s.read()
                with open(img, 'wb') as out_file:
                    out_file.write(data)
        return 'welcum to finland', img


@command
async def webm(board):
    'webms from 2ch.hk'
    if board == 'stats':
        text = ''
        for board in sosach.BOARDS+['f']:
            res = await sosach.all_webms(board)
            text += '{} - {}\n'.format(board, len(res))
        return text
    if not board:
        board = 'b'
    if board not in sosach.BOARDS and board not in ['f', 'fg']:
        return 'Boards are: {}'.format(' '.join(sosach.BOARDS))
    if board == 'f':
        res = await sosach.random_fap_webm()
    elif board == 'fg':
        res = await sosach.random_fap_webm(fg=True)
    else:
        res = await sosach.random_webm(board)
    if not res:
        return
    img = "tmp/video%s" % os.path.splitext(res[2])[1]
    async with aiohttp.ClientSession() as session:
        async with session.get(res[2]) as s:
            data = await s.read()
            with open(img, 'wb') as out_file:
                out_file.write(data)
    return res[0], img


@command
async def joke(arg):
    'Stupid jokes'
    jokesdb = json.load(open('jokes.json'))
    return random.choice(jokesdb)


@command(pass_data=True)
async def weather(data, region):
    'Weather'
    t = region or '%s, %s' % (regioncodes[data['country']], data['country_name'])
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'http://api.openweathermap.org/data/2.5/weather?appid={}&units=metric'.format(config.weather_key),
                params={'q': t}) as s:
            res = await s.json()
    out_message = "%s\nTemperature: %s C(burger %s F) Humidity: %s\n%s\nWind: %s m/s\nPressure: %s" % (
        res['name'], res['main']['temp'], 9.0 / 5.0 * res['main']['temp'] + 32, res['main']['humidity'],
        res['weather'][0]['description'], res['wind']['speed'], int(res['main']['pressure'] / 1.3332239))
    img = 'weathericons/%s.png' % res['weather'][0]['icon']
    return out_message, img


@command(pass_data=True)
async def time(data, region):
    'Time in region'
    if not region:
        region = u'{}, {}'.format(regioncodes[data['country']], data['country_name'])
    return wa(u'time in {}'.format(region))


@command
async def lurkers(arg):
    'Who\'s online'
    return os.popen('python ../lurkers.py | sort').read()


@command
async def urban(query):
    'Urban directory'
    res = ''
    for l in urbandict.define(query):
        res += "def: %s\nexample: %s\n" % (l['def'].strip(), l['example'].strip())
    return res or "Didn't find anything"


@command(to_convo='hangman', from_convo='hangman', pass_data=True)
async def play(data, arg):
    'Hangman game'
    return game.play(arg, data['identifier'], data['name'], data['country'])


@command
async def scores(arg):
    'Hangman scores'
    return game.stats()


@command
async def wa(query):
    'wolfram alpha'
    res = wolfram.query(query)
    out_message = u'\n'.join(z.text for z in list(res.pods)[1:] if z and z.text)
    out_message = out_message.replace('\:0440\:0443\:0431', '').replace('\:ffe5', '').replace('\:20b4', '')
    return out_message or "Didn't find anything"


@command(regex=r'\.(?:w|wiki)\s(.+)', command_name='wiki')
async def wiki(query):
    'wikipedia'
    if query.startswith('-'):
        lang, search = query.split(None, 1)
        lang = lang[1:]
        try:
            wikipedia.set_lang(lang)
            out_message = wikipedia.WikipediaPage(wikipedia.search(search)[0]).content
        except wikipedia.DisambiguationError as e:
            out_message = str(e)

    try:
        #out_message = wikipedia.summary(t.group(2), sentences=30)
        #out_message = wikipedia.WikipediaPage(query).content
        out_message = wikipedia.WikipediaPage(wikipedia.search(query)[0]).content
    except wikipedia.DisambiguationError as e:
        out_message = str(e)
    return out_message


@command
async def fortune(arg):
    'fortunes'
    return os.popen('fortune fortunes').read().strip()


@command
async def meme(arg):
    'memes'
    return '', 'memes/' + random.choice(os.listdir('memes'))


@command
async def kot(arg):
    'cat facts'
    out_message = random.choice(open('catfacts.txt').read().splitlines())
    img = 'cats/' + random.choice(os.listdir('cats'))
    return out_message, img


@command(regex=r'\.8ball(.+)?', command_name='8ball')
async def eightball(arg):
    '8ball'
    ball = ['it is certain', 'it is decidedly so', 'without a doubt', 'yes definitely',
            'you may rely on it', 'as i see, yes', 'most likely', 'outlook good', 'yes',
            'signs point to yes', 'reply hazy try again', 'ask again later', 'better not tell you now',
            'cannot predict now', 'concentrate and ask again', "don't count on it",
            'my reply is no', 'my sources say no', 'outlook not so good', 'very doubtful',
            'you should kill yourself', 'literally fuck off', 'how am i supposed to know', 'idk',
            'yeah, probably not', 'haha faggot no of course']
    return random.choice(ball)


# @command(regex=r'\.t\s(.+)')
@command(regex=r'\.t((\-[\S]+){0,1}\s[\s\S]+)')
async def t(arg):
    'translate'
    translator = YandexTranslate(config.yandex_translate_key)
    #    lang = translator.detect(arg)

    if arg.startswith('-'):
        lang, text = arg.split(None, 1)
        lang = lang[1:]
    else:
        text = arg
        lang = translator.detect(text)

    if lang != 'en':
        translation = translator.translate(text, '{}-en'.format(lang))['text'][0]
        answer = 'translated from {}\n{}'.format(lang, translation)
        return answer
    else:
        return "That's already English"


@command(regex=r'\.tts((\-[\S]+){0,1}\s[\s\S]+)', to_convo='tts')
async def tts(arg):
    'text to speech'
    # print 'arg: <'+arg+'>'
    # arg = arg.decode('utf-8').encode('utf-8')
    # print 'arg: ', arg
    if arg.strip() == 'languages':
        return '\n'.join('{}: {}'.format(*i) for i in sorted(gtts.lang.tts_langs().items()))

    if arg.startswith('-'):
        lang, text = arg.split(None, 1)
        lang = lang[1:]
    else:
        text = arg
        translator = YandexTranslate(config.yandex_translate_key)
        lang = translator.detect(text)

    if not lang in gtts.lang.tts_langs():
        lang = 'fi'

    tmp_ogg_file_path = 'tmp/tts.ogg'
    tts = gtts.gTTS(text=text, lang=lang, slow=False)
    tts.save(tmp_ogg_file_path)

    return gtts.lang.tts_langs().get(lang) + '\n' + text, tmp_ogg_file_path


@command
async def m(arg):
    'exchange rates'
    arg = arg.split()
    if not arg:
        return 'Missing arguments'
    fsym = arg[-1].upper()
    amount = float(arg[0]) if arg[0].isdigit() else 1
    api = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms=USD,EUR,GBP,RUB,UAH'
    async with aiohttp.ClientSession() as session:
        async with session.get(api.format(fsym)) as s:
            res = await s.json()
    return '{} {} is worth:\n'.format(amount, fsym) + '\n'.join('{} {}'.format(v * amount, k) for k, v in res.items())


@command(regex=r'(.*)(\s)(r8|rate)$', command_name='r8')
async def r8(arg):
    'rating rater'
    return 'I rate it %s/10' % random.randint(0, 11)


@command(regex=r'^(hi|hello|hehlo)$', command_name='hi', pass_data=True, ignore_case=True, hidden=True)
async def hi(data, arg):
    'say hi'
    for k, v in hellos.items():
        if data['country'].startswith(k):
            hello = v
            break
    else:
        hello = random.choice(list(hellos.values()))
    return "%s, %s!" % (hello, data['name'])


@command(regex=r'(^iwd$|lonely|gfless|i\swant\sdeath)', command_name='iwd', pass_data=True, ignore_case=True,
         hidden=True)
async def iwd(data, arg):
    'say iwd'
    return random.choice(['iktf', 'you have me', 'iwd', 'kys loser'])


@command
async def browsers(arg):
    'browser information'
    d = {}
    cursor = chat_db.find({})
    docs = await cursor.to_list(None)
    for post in docs:
        user_agent = post.get('user_agent', '')
        if user_agent:
            ua = ' '.join(word for word in
                          ['Chrome', 'Firefox', 'Opera', 'Mac OS', 'Windows', 'Android', 'Linux']
                          if word in user_agent)
            d[post['identifier']] = (
                post['name'], post.get('country', ''), ua
            )
    return '\n'.join(' '.join(p) for p in d.values())


@command
async def tarot(arg):
    'fortune telling'
    img, out_message = random.choice(tarot_cards)
    return out_message, 'tarot/{}'.format(img)


@command
async def telegram(arg):
    'link to telegram bot'
    if os.path.exists('../map/link.txt'):
        return open('../map/link.txt').read()
    else:
        return 'Link not found'


@command(regex=r'\.cowsay((\-[\S]+){0,1}\s[\s\S]+)', post_avatar=False)
async def cowsay(arg):
    'classic cowsay'
    if arg.strip() == 'cows':
        return ', '.join(cow.cow_options())

    if arg.startswith('-'):
        _cow, text = arg.split(None, 1)
        _cow = _cow[1:]
    else:
        text = arg
        _cow = 'www'

    if not _cow in cow.COWACTERS:
        _cow = 'www'

    return '[code]{}[/code]'.format(cow.COWACTERS[_cow]().milk(text))
