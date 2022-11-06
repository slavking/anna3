# coding: utf-8
import aiohttp
import shutil
import os
import re
import config
import random
from bs4 import BeautifulSoup
from html import unescape
import subprocess
import shlex

from livechanapi import post


async def process_links(data):
    out_message = ''
    img = ''
    message = data['body']
    convo = data['convo']

    image_ext = 'webm,mp4,png,jpg,jpeg,gif'.split(',')
    image_ext_dot = ['.' + e for e in image_ext]
    image_ext_or = '|'.join(image_ext)

    try:
        if "image" in data.keys():
            upload_file = data["image"]
            original_filename = data["image_filename"]
            extension = os.path.splitext(data["image"])[-1].lower()
        else:
            extension = ''

        if convo == "radio":
            t = re.compile(r'http[s]?:\/\/.*').match(message)
            if t and any(s in message for s in ('youtube', 'youtu.be',)):
                print('download youtube ' + t.group(0))
                # cmd = shlex.split('/home/ph/map/yt2playlist.sh "' + t.group(0) + '"')
                cmd = '/home/ph/radio/yt2playlist.sh "' + t.group(0) + '"'
                print('cmd:', cmd)
                env = dict(os.environ);
                env['LC_ALL'] = 'en_US.UTF-8'
                process = subprocess.Popen(cmd, shell=True, env=env)
                # process.wait()
                # os.system('/home/ph/map/yt2playlist.sh "'+t.match(0))+'"'
            else:
                if extension in [u'.mp3', u'.ogg']:
                    # filename = os.path.split(upload_file)[-1]
                    new_filename = u'/tmp/music/' + original_filename
                    shutil.copyfile(upload_file, new_filename)

                    print('download file ' + new_filename)
                    cmd = shlex.split('/home/ph/radio/mpc_do.sh add "' + 'tmp/' + original_filename + '"')
                    print('cmd:', cmd)
                    process = subprocess.Popen(cmd, shell=False)

        # link
        async with aiohttp.ClientSession() as session:
            t = re.compile(r'(http[s]?:\/\/.*)').match(message)
            if t and not any(
                    x in message for x in ['kotchan', 'youtube', 'youtu.be', 'twitter', 'instagram', 'krautchan', 'kohlchan']) and not \
            os.path.splitext(t.group(1).strip())[1] in image_ext_dot:
                async with session.head(t.group(1).strip()) as s:
                    if 'text/html' not in s.headers.get('content-type', '').lower():
                        return
                async with session.get(t.group(1).strip()) as s:
                    if s.status == 200:
                        res = await s.text()
                        # if s.encoding == 'ISO-8859-1':
                        #     res.encoding = 'utf-8'
                        title = BeautifulSoup(res).title.string
                        out_message = "Title: %s" % unescape(title)

            # webm link
            t = re.compile(r'(http[s]?:\/\/.*\.?({}))'.format(image_ext_or)).match(message)
            if t:
                img = "tmp/video%s" % os.path.splitext(t.group(1).strip())[1]
                async with session.get(t.group(1).strip()) as s:
                    filedata = await s.read()
                    with open(img, 'wb') as out_file:
                        out_file.write(filedata)

    except Exception as e:
        print(e)
        out_message = config.error_message

    if out_message or img:
        img = img or os.path.join(config.avatar_folder, random.choice(os.listdir(config.avatar_folder)))
        body = u'>>{}\n{}'.format(data['count'], out_message)
        await post(body, config.bot_name, data['convo'], config.bot_trip, img)
