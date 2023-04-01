import requests
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

    def check_character_valid(self, name, server):
# 캐릭터 명 유효성 확인
        body = '''{ characterData {
              character(name: "%s", serverSlug: "%s", serverRegion: "KR") {
                id
              }
            }}
          ''' % (name, server)

        self.user_id = json.loads(self.call_fflog_server(body))['data']['characterData']['character']['id']

        return

    def get_savage_raid_list(self):
# 레이드 종류 검색
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

        result = self.call_fflog_server(body)

        zones = json.loads(result)['data']['worldData']['expansion']['zones']

        for zone in zones:
            if len([difficulty for difficulty in zone['difficulties']
                    if difficulty['id'] == 101 and difficulty['sizes'] == [8]]) > 0:

                self.savages.append({
                    'name': zone['name'],
                    'encounters': zone['encounters']
                })

        return

    def get_recent_expansion(self):
# 최근 확장팩 정보 취득
        body = '''
        { 
            worldData {
                expansions {
                    id
                }
            } 
        }
        '''

        expansions = json.loads(self.call_fflog_server(body))['data']['worldData']['expansions']
        recent_expansion = sorted(expansions, key=lambda d: d['id'], reverse=True)
        self.recent_expansion = recent_expansion[0]['id']

    def get_party_member(self, code, fight_id):
# 파티원 직업 검색
        body = '''
        {
            reportData {
                report(code: "%s") {
                    rankings(fightIDs: [%d])
                }
            }
        }

        ''' % (code, fight_id)

        party_member = json.loads(self.call_fflog_server(body))['data']['reportData']['report']['rankings']['data'][0]['roles']
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

    def get_parse_data(self, encounter_id):
        body = '''{ characterData {
              character(id: %d) {
                encounterRankings(encounterID: %d, difficulty: 101, metric: rdps)
              }
            }}
          ''' % (self.user_id, encounter_id['id'])

        result = json.loads(self.call_fflog_server(body))
        data = result['data']['characterData']['character']['encounterRankings']
        if not ('error' in data.keys()):

            analasys = Analysis(data, self)
            return {'name': encounter_id['name'], 'data': analasys.get_highest_parse()}
        return

    def classify_by_season(self):

        result_set = []

        if len(self.savages) > 0:
            for savage in self.savages:
                for encounter in savage['encounters']:
                    parse_data = self.get_parse_data(encounter)
                    if parse_data is not None:
                        result_set.append(parse_data)

        return result_set

    def call_fflog_server(self, query):
        data = requests.get('https://www.fflogs.com/api/v2/client',
                            headers={'Authorization': 'Bearer {}'.format(self.token),
                                     'Content-Type': 'application/json'},
                            json={"query": query})

        return data.content.decode('utf-8')
# fflog 서버 호출
