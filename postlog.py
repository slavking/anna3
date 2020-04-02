import aiosqlite
import os
import re
from datetime import datetime, date


async def log_post(data):
    # col = pymongo.MongoClient().livechan_db.stat
    # col.update_one({'ident': data['identifier'], 'date': date.today().strftime('%Y-%m-%d')},
    #     {
    #         '$set': {'country': data['country'], 'country_name': data['country_name'], 'name': data['name']},
    #         '$inc': {'count': 1}
    #     },
    #     upsert=True
    # )
    if not os.path.exists('lb.sqlite'):
        async with aiosqlite.connect('lb.sqlite') as conn:
            for line in """
                CREATE TABLE posts (id INTEGER PRIMARY KEY, ident TEXT, name TEXT, trip TEXT, convo TEXT, text TEXT, date TEXT, country, country_name);
                CREATE TABLE games (id INTEGER PRIMARY KEY, ident TEXT, status TEXT, date TEXT, name, country);
                CREATE INDEX ident_index on posts(ident);
                CREATE INDEX date_index on posts(date);
                CREATE TABLE stickers(name);
            """.splitlines():
                await conn.execute(line)

    if data['body'].strip().startswith('.') or 'country_name' not in data or 'country' not in data:
        return

    async with aiosqlite.connect('lb.sqlite') as conn:
        await conn.execute(
            'INSERT INTO posts(id,ident,name,trip,convo,text,country,country_name,date) VALUES(?,?,?,?,?,?,?,?,?);',
            (data['count'], data['identifier'], data['name'], data.get('trip', ''), data['convo'], '', data['country'], data['country_name'], datetime.now()))
        for st in re.findall(r'\[st\]([\w\d\-\.]+)\[\/st\]', data['body']):
            await conn.execute('INSERT INTO stickers(name) VALUES(?)', (st,))
