import asyncio
import os
import random

import config
from commands import kc
from livechanapi import post


async def hourly():
    while True:
        file = os.path.join('webms/', random.choice(os.listdir('webms/')))
        body = await kc('')
        await post(body, config.bot_name, 'General', config.bot_trip, file)
        await asyncio.sleep(60*60)
