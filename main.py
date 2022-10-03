# This is a sample Python script.

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


def main(name, server):
    print("start_parse")
    fflog = Fflog()
    print('get token')
    fflog.check_character_valid(name, server)
    print('get user')
    fflog.get_recent_expansion()
    print('get expansion')
    fflog.get_savage_raid_list()
    print('get raid data')
    output = {'parse_result': fflog.classify_by_season()}
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
    if not message.author.bot and split_message[0] == '/ff':
        if split_message[1] in env.SERVER:
            text = main(split_message[2], env.SERVER[split_message[1]])['parse_result']
            print("system_call")
            flag = True
            for i in text:
                if flag:
                    await message.channel.send("`" + i['name'] + "`")
                    for parse_data in i['data']:
                        await message.channel.send(formatting_raw(parse_data))
                    if text[-1] == i:
                        flag = False


client.run(env.DISCORD_TOKEN)



