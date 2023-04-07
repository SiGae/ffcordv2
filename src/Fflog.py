import asyncio
import logging
import aiohttp

from Analysis import Analysis
from env import FFLOG_CLIENT, FFLOG_SECRET, CLIENT_URL, TOKEN_URL, JOB_KEY, JOB_SHORT, BASE_URL


class Fflog:
    token = None
    user_id = None
    recent_expansion = 1
    savages = []

    encounters_dict : dict = {}
    savage_name_from_key = {}

    # oAUTH2 토큰 취득
    @classmethod
    async def getToken(cls):
        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL,
                                    data={"grant_type": "client_credentials"},
                                    auth=aiohttp.BasicAuth(
                                        FFLOG_CLIENT, FFLOG_SECRET)) as resp:
                cls.token = (await resp.json())["access_token"]

    # 캐릭터 명 유효성 확인
    async def check_character_valid(self, name, server):
        body = '''{ characterData {
              character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                id
              }
            }}
          ''' % (name, server)

        self.user_id = (
            await self._get(body))['data']['characterData']['character']['id']

        return

    # 레이드 종류 검색
    @classmethod
    async def get_savage_raid_list(cls):
        # 확장팩 내 전퉅 인스턴스
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

        zones = (await
                 cls._get(body))['data']['worldData']['expansion']['zones']

        # 영웅난이도 8인레이드 중 가장 최신 레이드를 가져옵니다.
        cls.savages = next((zone['encounters'] for zone in zones if any(difficulty['id'] == 101 and difficulty['sizes'] == [8] for difficulty in zone['difficulties'])), None)
        cls.savage_name_from_key = {str(savage['id']): savage['name'] for savage in cls.savages}

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

        expansions = (await cls._get(body))['data']['worldData']['expansions']
        recent_expansion = sorted(expansions,
                                  key=lambda d: d['id'],
                                  reverse=True)
        cls.recent_expansion = recent_expansion[0]['id']

    async def get_parse_data(self, name, server):
        query_list = []
        key_back = {}

        # 검색 쿼리 생성
        for savage in self.savages:
            query_list.append(
                f'a{savage["id"]}: encounterRankings(encounterID: {savage["id"]}, difficulty: 101, metric: rdps)'
            )
            key_back[f'a{savage["id"]}'] = savage["name"]

        # 쿼리 결합
        body = '''{ characterData {
              character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                %s
              }
            }}
          ''' % (name, server, '\n'.join(query_list))

        # 검색
        result = await self._get(body)

        # 정상일 경우
        if not ('error' in result.keys()):
            # 결과
            self.encounters_dict = {key.replace('a', ''): encounter['ranks'] for key, encounter in result['data']['characterData']['character'].items()}
        return

    async def get_score(self, name, highest_list):
        party_info = [self._get_log_info(highest_log) for highest_log in highest_list]

        return {'name': self.savage_name_from_key[name], 'data': await asyncio.gather(*party_info)}


    # 파티 정보 정리
    async def _get_log_info(self, log):
        log['파티구성'] = await self._get_party_member(log['code'], log['id'])
        log['직업'] = log['job']
        del log['code']
        del log['id']
        del log['job']

        return log

    # 파티원 직업 검색
    async def _get_party_member(self, report_code, fight_id):
        body = '''
        {
            reportData {
                report(code: "%s") {
                    rankings(fightIDs: [%d])
                }
            }
        }

        ''' % (report_code, fight_id)

        party_member = (
            await self._get(body)
        )['data']['reportData']['report']['rankings']['data'][0]['roles']

        classes = [
            JOB_KEY[user_class['class']]
            for class_group, class_data in party_member.items()
            for user_class in class_data['characters']
        ]

        return ''.join([JOB_SHORT[each_class] for each_class in sorted(list(set(classes)))])

    # 최근 레이드 기준 검색
    async def classify_by_season(self, name, server):
        if len(self.savages) > 0:
            await self.get_parse_data(name, server)

            return await asyncio.gather(*[
                self.get_score(encounter_id)
                for encounter_id in self.encounters_dict.keys()
            ])

    # fflog 서버 호출
    @classmethod
    async def _get(cls, query):

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{CLIENT_URL}',
                                   headers={
                                       'Authorization': f'Bearer {cls.token}',
                                       'Content-Type': 'application/json'
                                   },
                                   json={"query": query}) as resp:
                try:
                    response_content = await resp.json()
                except Exception:
                    logger = logging.getLogger()
                    logger.exception('Failed to read response data')
                finally:
                    return response_content
