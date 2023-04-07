import asyncio
import discord

import env
from Fflog import Fflog
from Analysis import Analysis


async def main(name, server):
    print("start_parse")
    fflog = Fflog()

    # 전체 레이드 데이터 추출
    await fflog.get_parse_data(name, server)

    # 직업별 최고기록 추출
    highest_log_dict = {
        encounter_id: await Analysis(encounter_id, fflog).get_highest_parse()
        for encounter_id in fflog.encounters_dict
    }

    # 파티구성 취득
    return await asyncio.gather(*[
        fflog.get_member_info(encounter_id, logs)
        for encounter_id, logs in highest_log_dict.items()
    ])


async def refresh_token():
    while True:
        await Fflog.getToken()
        await Fflog.get_recent_expansion()
        await Fflog.get_savage_raid_list()
        await asyncio.sleep(3600)


async def message_formatter(data: dict):
    text = [
        f'\nBest: {str(log_list["점수"])} | {str(log_list["파티구성"])} | {str(log_list["직업"])} '
        for log_list in data['data']
    ]
    return '```markdown\n' + '# ' + data['name'] + '\n' + ''.join(text) + '```'


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    split_message = message.content.split()
    if not message.author.bot and (split_message[0] == '/ff'
                                   and split_message[1] in env.SERVER):

        # 게임 데이터 취득
        encounter_logs = await main(split_message[2],
                                    env.SERVER[split_message[1]])

        # 메시지 포매팅
        formatted_message = await asyncio.gather(*[
            message_formatter(encounter_log)
            for encounter_log in encounter_logs
        ])
        await message.channel.send('\n'.join(formatted_message))


loop = asyncio.get_event_loop()
loop.create_task(refresh_token())
loop.create_task(asyncio.to_thread(client.run, env.DISCORD_TOKEN))
loop.run_forever()
