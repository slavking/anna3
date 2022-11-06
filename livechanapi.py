# coding: utf-8
import aiohttp, asyncio
from urllib.parse import urljoin
from functools import partial
import os
import config

COOKIES = {'password_livechan': config.password_livechan}

async def post(body, name="Anonymous", convo="General", trip="", file="", country=None):
    if trip:
        name = '{}##{}'.format(name, trip)
    data = {
        'chat': config.board,
        'name': name,
        'trip': trip,
        'body': body,
        'convo': convo,
    }
    if country:
        data['country'] = country
    if file:
        data['image'] = open(file, 'rb')
    async with aiohttp.ClientSession(cookies=COOKIES) as session:
        await session.post(
                f'https://{config.url}/chat/{config.board}',
                data=data
            )


async def get_posts(last_count=0, limit=30):
    params = {'count': last_count, 'limit': limit}
    async with aiohttp.ClientSession(cookies=COOKIES) as session:
        async with session.get(f'https://{config.url}/last/{config.board}', params=params) as s:
            data = await s.json()
            data.reverse()
            return data


async def updater(callback):
    data = await get_posts(0, 1)
    last_count = data[0]['count']
    while True:
        try:
            await asyncio.sleep(config.poll_interval)
            data = await get_posts(last_count)
            for post_data in data:
                await callback(post_data)
                last_count = post_data['count']
        except Exception as e:
            import traceback
            traceback.print_exc()