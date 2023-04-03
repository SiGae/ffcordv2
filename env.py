import os

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
FFLOG_CLIENT = os.environ.get('FFLOG_CLIENT')
FFLOG_SECRET = os.environ.get('FFLOG_SECRET')

BASE_URL = 'https://www.fflogs.com/'
TOKEN_URL = BASE_URL + 'oauth/token'
CLIENT_URL = BASE_URL + 'api/v2/client'

SERVER = {
    '모그리': 'moogle',
    '초코보': 'chocobo',
    '카벙클': 'carbuncle',
    '톤베리': 'tonberry',
    '펜리르': 'fenrir'
}

JOB = {
    'Astrologian': '점성술사',
    'Bard': '음유시인',
    'BlackMage': '흑마도사',
    'DarkKnight': '암흑기사',
    'Dragoon': '용기사',
    'Machinist': '기공사',
    'Monk': '몽크',
    'Ninja': '닌자',
    'Paladin': '나이트',
    'Scholar': '학자',
    'Summoner': '소환사',
    'Warrior': '전사',
    'WhiteMage': '백마도사',
    'RedMage': '적마도사',
    'Samurai': '사무라이',
    'Dancer': '무도가',
    'Gunbreaker': '건브레이커',
    'Reaper': '리퍼',
    'Sage': '현자'
}

JOB_KEY = {
    'Astrologian': 5,
    'Bard': 16,
    'BlackMage': 18,
    'DarkKnight': 1,
    'Dragoon': 11,
    'Machinist': 15,
    'Monk': 10,
    'Ninja': 12,
    'Paladin': 4,
    'Scholar': 7,
    'Summoner': 19,
    'Warrior': 2,
    'WhiteMage': 6,
    'RedMage': 17,
    'Samurai': 9,
    'Dancer': 14,
    'Gunbreaker': 3,
    'Reaper': 13,
    'Sage': 8
}

JOB_SHORT = {
    1: '암',
    2: '전',
    3: '건',
    4: '나',
    5: '점',
    6: '백',
    7: '학',
    8: '현',
    9: '사',
    10: '몽',
    11: '용',
    12: '닌',
    13: '리',
    14: '무',
    15: '기',
    16: '음',
    17: '적',
    18: '흑',
    19: '솬'
}
