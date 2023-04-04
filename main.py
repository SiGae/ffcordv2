import asyncio
import os

import env
import discord
from multiprocessing import Process
from Fflog import Fflog


async def formatting_raw(raw):
    score = "> `점수` : `" + str(raw['점수']) + "`\n"
    party_member = "> `파티구성` : `" + str(raw['파티구성']) + "`\n"
    job = "> `직업` : `" + str(raw['직업']) + "`"

    return score + party_member + job


async def main(name, server):
    print("start_parse")
    fflog = Fflog()

    # setup = [fflog.check_character_valid(name, server)]
    # await fflog.check_character_valid(name, server)

    return await fflog.classify_by_season(name, server)


async def refresh_token():
    while True:
        await Fflog.getToken()
        await Fflog.get_recent_expansion()
        await Fflog.get_savage_raid_list()
        await asyncio.sleep(3600)


async def send_msg(data: dict):
    result_text = "`" + data['name'] + "`\n"
    text = await asyncio.gather(*[formatting_raw(log_list) for log_list in data['data']])

    return result_text + '\n'.join(text)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    split_message = message.content.split()
    if not message.author.bot and (split_message[0] == '/ff' and split_message[1] in env.SERVER):
        result = (await main(split_message[2], env.SERVER[split_message[1]]))
        pre = await asyncio.gather(*[send_msg(floor) for floor in result])
        await message.channel.send('\n'.join(pre))


loop = asyncio.get_event_loop()
loop.create_task(refresh_token())
loop.create_task(asyncio.to_thread(client.run, env.DISCORD_TOKEN))
loop.run_forever()

