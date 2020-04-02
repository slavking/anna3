import random
import asyncio
import motor.motor_asyncio
from livechanapi import post
import config

col = motor.motor_asyncio.AsyncIOMotorClient().livechan_db.chat_dbs


async def fake_mirri(data):
    if random.randint(0, 10) != 1 or data['convo'] != 'General':
        return
    body = ">>{}\n{}".format(data['count'], random.choice(['k', 'yeah)', 'bad=good', "k=yeah)", "good=bad", "hello"]))
    await asyncio.sleep(random.random() * 15)
    await post(body, 'Mirri', data['convo'], country='FI-15')


async def fake_post(data):
    friendly_replies = [
        'kys',
        'this. so much this.',
        'oh god',
        'creepy incel basterd',
        'tnx',
        'me',
        'why worry',
        'idk',
        'soon',
        'so what?',
        'really?',
        'yes. why?',
        'cute',
        'all me',
        'bot',
        'thanks',
        'no u',
        'no me',
        'cuck',
        'Patryk Adamczyk insults Ukrainians and disabled people for no reason',
        "I'm disabled",
        'its dont',
        'well',
        'hot',
        'hi',
        'you are a good kind of kot',
        'this',
        'wow',
        'I posted this',
    ]
    friendly_stickers = [
        '[st]apu-1479727845001[/st]',
        '[st]apu-1479764034003[/st]',
        '[st]apu-1479755144003[/st]',
        '[st]kot-wageslave[/st]',
        '[st]apu-1479763892003[/st]',
        '[st]apu-1479729971002[/st]',
        '[st]apu-1479764034003[/st]',
    ]
    friendly_posters = [
        ('AR-07', 'ARKot', ''),
        ('GB', 'Anse/Egor', 'opinion'),
        ('RU-48', 'Egor/Anse', 'lopinion'),
        ('HU-05', 'GNU/Macska', ''),
        ('PL-77', '', 'secretworry'),
        ('RU-66', 'Tomsk', ''),
        ('RU-71', '', 'ekb'),
        ('NL-05', 'whiskey-drinking piano-playing nigger', ''),
        ('ES-32', 'Gato', ''),
        ('UA-12', 'yaro', ''),
        ('RS-00', 'spinosaurus', 'croc'),
        ('IT-09', u'(= ゜ω ゜ )~♥', 'lombard'),
        ('US-IN', 'corn', ''),
        ('PL-78', u'Agata to słodziak', 'wojak'),
        ('RU-47', 'true muscovy', ''),
        ('DK', 'Visigoth', ''),
    ]
    out_message = ''

    if random.randint(1, 50) == 13:
        topost = random.choice(['sticker', 'post', 'reply'])
        if topost == 'post':
            cursor = col.find({})
            docs = await col.to_list(None)
            while not out_message:
                out_message = random.choice(docs)['body']
                out_message = '\n'.join(line for line in out_message.splitlines() if not line.startswith('>'))
        elif topost == 'sticker':
            out_message = random.choice(friendly_stickers)
        else:
            out_message = random.choice(friendly_replies)
        body = u'>>{}\n{}'.format(data['count'], out_message)
        country, name, trip = random.choice(friendly_posters)
        if trip:
            name = '{}#{}'.format(name, trip)
        await asyncio.sleep(random.random()*15)
        await post(body, name, data['convo'], '', '', country)
