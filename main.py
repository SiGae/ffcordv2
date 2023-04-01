# This is a sample Python script.
import asyncio
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import requests
import env
import discord
from Fflog import Fflog


def formatting_raw(raw):
    score = "> `점수` : `" + str(raw['점수']) + "`\n"
    party_member = "> `파티구성` : `" + str(raw['파티구성']) + "`\n"
    job = "> `직업` : `" + str(raw['직업']) + "`"

    return score + party_member + job


async def main(name, server):
    print("start_parse")
    fflog = Fflog()
    print('get token')

    setup = [fflog.check_character_valid(name, server), fflog.get_recent_expansion()]
    await asyncio.gather(*setup)
    await fflog.get_savage_raid_list()
    print('get raid data')
    output = {'parse_result': await fflog.classify_by_season()}
    print("end_parse")

    return output


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
        print(split_message[2])
        print(env.SERVER[split_message[1]])
        text = (await main(split_message[2], env.SERVER[split_message[1]]))['parse_result']
        flag = True
        for i in text[0]:
            if flag:
                print(i)
                await message.channel.send("`" + i['name'] + "`")
                for parse_data in i['data']:
                    await message.channel.send(formatting_raw(parse_data))
                if text[-1] == i:
                    flag = False


client.run(env.DISCORD_TOKEN)



