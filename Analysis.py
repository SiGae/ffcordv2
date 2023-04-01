import math
from itertools import groupby
from operator import itemgetter
from env import JOB


class Analysis:
    def __init__(self, raw_data, fflog):
        self.raw_data = raw_data
        self.fflog = fflog

    async def get_highest_parse(self):
        ranks = self.raw_data['ranks']
        parse_list = []
        for rank in ranks:
            parse_list.append({
                'code': rank['report']['code'],
                'id': rank['report']['fightID'],
                'job': JOB[rank['spec']],
                '점수': math.trunc(rank['historicalPercent'] * 10) / 10
            })

        highest_list = []

        parse_list.sort(key=itemgetter('job'))
        grouped_list = []
        for i, g in groupby(parse_list, key=itemgetter("job")):
            grouped_list.append(list(g))

        for job in grouped_list:
            highest_list.append(max(job, key=lambda x: x['job']))

        for i in highest_list:
            i['파티구성'] = await self.fflog.get_party_member(i['code'], i['id'])
            i['직업'] = i['job']
            del i['code']
            del i['id']
            del i['job']

        return highest_list




