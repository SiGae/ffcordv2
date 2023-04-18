# FFcord
## 디스코드용 FFlogs 검색 봇

## 실행 방법
* poetry가 설치된 환경에서 실행시
  * DISCORD_TOKEN, FFLOG_CLIENT, FFLOG_SECRET 환경변수에 값을 입력해줍니다.
  * `poetry install`명령어로 의존성 라이브러리들을 설치합니다.
  * `poetry run python main.py` 명령어로 실행합니다.

## 사용 기술: 
* Python 3.9
* [discord.py](https://github.com/Rapptz/discord.py)
* asyncio
* GraphQL
* yapf
* Docker

## Docker image 
> https://hub.docker.com/repository/docker/sigae/ffcord

## 기능 개발 및 베타 테스트용 디스코드
> https://discord.gg/HeMrpmrhXT

## UPDATE

> 2023-04-01 ~ 2023-04-07
>> 복수 호출로 인한 처리지연 문제 해결
>>> * asyncio.gather를 활용하여 api 복수 호출 시간 단축
>>> * graphQL alias 기능 활용하여 호출 api 최소화
      >>> 약 30초 -> 2초로 속도 단축


> 2022-10-02 
>> init

## Special thanks
* [시앨@모그리](https://www.fflogs.com/character/kr/moogle/%ec%8b%9c%ec%95%a8)
* [루첸트@모그리](https://www.fflogs.com/character/kr/moogle/%eb%a3%a8%ec%b2%b8%ed%8a%b8)
