# coding: utf-8
import re
import os
import random
import config
import aiohttp
from livechanapi import post


commands = []


def command(regex=None, pass_data=False, to_convo=None, from_convo=None, command_name='__default__', post_avatar=True):
    def decorator(func):
        reg = re.compile(r'\.{}$|\.{}\s(.+)'.format(func.__name__, func.__name__))
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
                    res = config.error_message
                if not res:
                    return
                elif type(res) in (str,):
                    body, file = res, None
                else:
                    body, file = res
                if not file and post_avatar:
                    file = os.path.join('avatars/', random.choice(os.listdir('avatars/')))
                body = u'>>{}\n{}'.format(data['count'], body)
                await post(body, config.bot_name, to_convo if to_convo else data['convo'], config.bot_trip, file)
                return match

        callback.__doc__ = func.__doc__
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
    out_message = 'Commands are:\n'
    out_message += '\n'.join(['{} - {}'.format(cmd.__name__, cmd.__doc__) for cmd in commands])
    return out_message


@command
async def bible(arg):
    'Bible quote'
    async with aiohttp.ClientSession() as sess:
        async with sess.get('http://labs.bible.org/api/?passage=random') as res:
            text = await res.text()
        text = text.replace('<', '[').replace('>', ']')
        return text


@command(regex=r'.\random\s(\d+)$', command_name='random')
async def random(arg):
    'random. usage: random max_number'
    arg = int(arg)
    return str(random.randint(0, arg))


@command(regex=r'^([Hh]i|[Hh]ello|[Hh]ehlo)$', command_name='hi', pass_data=True)
async def hi(data, arg):
    'says hi'
    return "%s, %s!" % (random.choice(['Hi', 'Hello', 'Privet', 'Hola', 'Bonjour', 'Hallo']), data['name'])

