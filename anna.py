# coding: utf-8
import argparse
import livechanapi
import config
import commands
import postlog
import fakeposter
import hourly
import links
import aiohttp
import asyncio
# import push

loop = asyncio.get_event_loop()


async def process_chat(data):
    # push.push(data)

    if data.get('trip') == config.bot_trip_encoded and data['name'] == config.bot_name:
        return

    await postlog.log_post(data)

    for command in commands.commands:
        loop.create_task(command(data))

    loop.create_task(links.process_links(data))
    # await fakeposter.fake_mirri(data)
    # await fakeposter.fake_post(data)


if __name__ == '__main__':
    # import signalhandler
    loop.create_task(hourly.hourly())
    loop.run_until_complete(livechanapi.updater(process_chat))
