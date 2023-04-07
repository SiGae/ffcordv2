import asyncio
import math
from itertools import groupby
from operator import itemgetter
import env


class Analysis:

    def __init__(self, encounter_id, fflog):
        self.encounter_id = encounter_id
        self.fflog = fflog

    # 최고 점수만 추출
    async def get_highest_parse(self):
        parse_list = []
        for rank in self.fflog.encounters_dict[self.encounter_id]:
            parse_list.append({
                'code':
                rank['report']['code'],
                'id':
                rank['report']['fightID'],
                'job':
                env.JOB[rank['spec']],
                '점수':
                math.trunc(rank['historicalPercent'] * 10) / 10
            })

        parse_list.sort(key=itemgetter('job'))

        return [
            max(list(logs), key=lambda x: x['점수'])
            for job_name, logs in groupby(parse_list, key=itemgetter("job"))
        ]
