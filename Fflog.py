import asyncio
import logging

import requests
import aiohttp
import json
from Analysis import Analysis

from env import FFLOG_CLIENT, FFLOG_SECRET, CLIENT_URL, TOKEN_URL, JOB_KEY, JOB_SHORT


class Fflog:
    token = None
    user_id = None
    recent_expansion = None
    savages = []

    def __init__(self):
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(FFLOG_CLIENT, FFLOG_SECRET),
        )
        self.token = response.json()["access_token"]

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
    async def get_savage_raid_list(self):
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
        ''' % self.recent_expansion


        zones = (await self.call_fflog_server(body))['data']['worldData']['expansion']['zones']

        for zone in zones:
            if len([difficulty for difficulty in zone['difficulties']
                    if difficulty['id'] == 101 and difficulty['sizes'] == [8]]) > 0:

                self.savages.append({
                    'name': zone['name'],
                    'encounters': zone['encounters']
                })

        return

# 최근 확장팩 정보 취득
    async def get_recent_expansion(self):
        body = '''
        { 
            worldData {
                expansions {
                    id
                }
            } 
        }
        '''

        expansions = (await self.call_fflog_server(body))['data']['worldData']['expansions']
        recent_expansion = sorted(expansions, key=lambda d: d['id'], reverse=True)
        self.recent_expansion = recent_expansion[0]['id']

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

    async def get_parse_data(self, encounter_id):
        body = '''{ characterData {
              character(id: %d) {
                encounterRankings(encounterID: %d, difficulty: 101, metric: rdps)
              }
            }}
          ''' % (self.user_id, encounter_id['id'])

        result = await self.call_fflog_server(body)
        data = result['data']['characterData']['character']['encounterRankings']
        if not ('error' in data.keys()):

            analasys = Analysis(data, self)
            return {'name': encounter_id['name'], 'data': await analasys.get_highest_parse()}
        return

    async def classify_by_season(self):

        result_set = []

        if len(self.savages) > 0:
            for savage in self.savages:
                savage_encounter = []
                for encounter in savage['encounters']:
                    savage_encounter.append(self.get_parse_data(encounter))
                result_set.append(await asyncio.gather(*savage_encounter))

        return result_set

# fflog 서버 호출
    async def call_fflog_server(self, query):

        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.fflogs.com/api/v2/client', headers={'Authorization': 'Bearer {}'.format(self.token), 'Content-Type': 'application/json'}, json={"query": query}) as resp:
                try:
                    response_content = await resp.json()
                except Exception:
                    logger = logging.getLogger()
                    logger.exception('Failed to read response data')
                finally:
                    return response_content
