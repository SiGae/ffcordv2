import asyncio
import logging

import requests
import aiohttp
from Analysis import Analysis

from env import FFLOG_CLIENT, FFLOG_SECRET, CLIENT_URL, TOKEN_URL, JOB_KEY, JOB_SHORT, BASE_URL


class Fflog:
    token = None
    user_id = None
    recent_expansion = None
    savages = []

    @classmethod
    async def getToken(cls):
        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL,
                                    data={"grant_type": "client_credentials"},
                                    auth=aiohttp.BasicAuth(FFLOG_CLIENT, FFLOG_SECRET)
                                    ) as resp:
                cls.token = (await resp.json())["access_token"]

# 캐릭터 명 유효성 확인
    async def check_character_valid(self, name, server):
        body = '''{ characterData {
              character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                id
              }
            }}
          ''' % (name, server)

        self.user_id = (await self.call_fflog_server(body))['data']['characterData']['character']['id']

        return

# 레이드 종류 검색
    @classmethod
    async def get_savage_raid_list(cls):
        body = '''
            {
                worldData {
                    expansion(id: %d) {
                        zones {
                            id      
                            name
                            difficulties {
                                id
                                sizes
                            }
                            encounters {
                                id
                                name
                            }
                        }
                    }
                }
            }
        ''' % cls.recent_expansion

        zones = (await cls.call_fflog_server(body))['data']['worldData']['expansion']['zones']

        for zone in zones:
            if len([difficulty for difficulty in zone['difficulties']
                    if difficulty['id'] == 101 and difficulty['sizes'] == [8]]) > 0:

                cls.savages.append({
                    'name': zone['name'],
                    'encounters': zone['encounters']
                })

        return

# 최근 확장팩 정보 취득
    @classmethod
    async def get_recent_expansion(cls):
        body = '''
        { 
            worldData {
                expansions {
                    id
                }
            } 
        }
        '''

        expansions = (await cls.call_fflog_server(body))['data']['worldData']['expansions']
        recent_expansion = sorted(expansions, key=lambda d: d['id'], reverse=True)
        cls.recent_expansion = recent_expansion[0]['id']

    async def get_party_info(self, log):
        log['파티구성'] = await self.get_party_member(log['code'], log['id'])
        log['직업'] = log['job']
        del log['code']
        del log['id']
        del log['job']

        return log

# 파티원 직업 검색
    async def get_party_member(self, code, fight_id):
        body = '''
        {
            reportData {
                report(code: "%s") {
                    rankings(fightIDs: [%d])
                }
            }
        }

        ''' % (code, fight_id)
        party_member = (await self.call_fflog_server(body))['data']['reportData']['report']['rankings']['data'][0]['roles']
        classes = []

        for class_group, class_data in party_member.items():
            self._get_class(class_data, classes)

        classes = sorted(list(set(classes)))

        result_set = []
        for each_class in classes:
            result_set.append(JOB_SHORT[each_class])

        return ''.join(result_set)

    def _get_class(self, class_type, classes: list):
        for character in class_type['characters']:
            classes.append(JOB_KEY[character['class']])

        return classes

    async def get_parse_data(self, encounters, name, server):
        query_list = []
        key_back = {}
        for encounter in encounters:
            query_list.append(f'a{encounter["id"]}: encounterRankings(encounterID: {encounter["id"]}, difficulty: 101, metric: rdps)')
            key_back[f'a{encounter["id"]}'] = encounter["name"]

        body = '''{ characterData {
              character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                %s
              }
            }}
          ''' % (name, server, '\n'.join(query_list))

        result = await self.call_fflog_server(body)

        response = []

        if not ('error' in result.keys()):
            response = await asyncio.gather(*[self.get_score(key_back[key], Analysis(encounter, self)) for key, encounter in result['data']['characterData']['character'].items()])

        return response

    async def get_score(self, name: str, analysis: Analysis):
        return {'name': name, 'data': await analysis.get_highest_parse()}

    async def classify_by_season(self, name, server):
        if len(self.savages) > 0:

            # savage_list = self.get_parse_data(self.savages[0]['encounters'], name, server)
            # print(await self.get_parse_data(self.savages[0]['encounters'], name, server))

            return await self.get_parse_data(self.savages[0]['encounters'], name, server)

# fflog 서버 호출
    @classmethod
    async def call_fflog_server(cls, query):

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{CLIENT_URL}', headers={'Authorization': 'Bearer {}'.format(cls.token), 'Content-Type': 'application/json'}, json={"query": query}) as resp:
                try:
                    response_content = await resp.json()
                except Exception:
                    logger = logging.getLogger()
                    logger.exception('Failed to read response data')
                finally:
                    return response_content
