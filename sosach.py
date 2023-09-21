# coding: utf-8
import aiohttp
from urllib.parse import urljoin
import random

BOARDS = ['au', 'c', 'mlp', 'mov', 'sci', 'spc', 'gd', 'v', 'a', 'b', 'int', 'wm', 'tv']
FAPBOARDS = ['b', 'a', 'hc', 'e', 'gg', 'int', 'mov']
WORDS = ['webm', u'шebm', 'mp4', u'шебм', u'цуиь']
FAPWORDS = ['fap', u'фап', 'porn', u'порн', u'прон', 'hentai']
NOWORDS = []


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, verify_ssl=False) as s:
            if s.status != 200:
                return None
            return await s.json()


async def webm_threads(board='b'):
    t = await get_json('https://2ch.hk/%s/catalog.json' % board)
    t = t['threads']
    return [x['num'] for x in t if any(word in x['subject'].lower() for word in WORDS) and not any(word in x['subject'].lower() for word in NOWORDS)]


async def fap_threads(fg=False):
    res = []
    for board in FAPBOARDS if not fg else ['fg']:
        t = await get_json('https://2ch.hk/%s/catalog.json' % board)
        t = t['threads']
        for x in t:
            text = x['subject'].lower()+'\n'+x['comment'].lower()
            if any(word in text for word in FAPWORDS):
                res.append((board, x['num']))
    return res


async def files(board, num):
    tr = await get_json('https://2ch.hk/%s/res/%s.json' % (board, num))
    if not tr:
        return []
    res = []
    posts = tr['threads'][0]['posts']
    for post in posts:
        posts = post.get('files') or []
        for f in posts:
            if f['path'].endswith('mp4') or f['path'].endswith('webm'):
                res.append((f.get('fullname', 'video'), 'https://2ch.hk/%s/res/%s.html#%s' % (board, num, post['num']), urljoin('https://2ch.hk/',f['path'])))
    return res


async def random_webm(board='b'):
    webms = []
    threads = await webm_threads(board)
    for num in threads:
        res = await files(board, num)
        webms.extend(res)
    return webms and random.choice(webms) or None


async def random_fap_webm(fg=False):
    threads = await fap_threads(fg)
    webms = []
    while threads and not webms:
        board, num = threads.pop(random.randint(0, len(threads)-1))
        webms = await files(board, num)
    return webms and random.choice(webms) or None


async def all_webms(board):
    webms = []
    if board == 'f':
        threads = await fap_threads()
    else:
        threads = await webm_threads(board)
        threads = [(board, tr) for tr in threads]
    for board, tr in threads:
        res = await files(board, tr)
        webms.extend(res)
    return webms
