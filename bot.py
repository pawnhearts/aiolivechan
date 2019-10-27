# coding: utf-8
import argparse
import livechanapi
import config
import commands
import aiohttp
import asyncio

loop = asyncio.get_event_loop()

async def process_chat(data):

    if data.get('trip') == config.bot_trip_encoded and data['name'] == config.bot_name:
        return

    for command in commands.commands:
        loop.create_task(command(data))

if __name__ == '__main__':
    loop.run_until_complete(livechanapi.updater(process_chat))
