import requests
import datetime
from dotenv import load_dotenv
import math
from os import getenv
from discord import Webhook
import asyncio
import aiohttp

load_dotenv()

url="https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&current=temperature_2m,precipitation,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo&forecast_days=5"
debug_url="http://127.0.0.1:3000/debug.json"

def images(code,daytime):
    data1 = None
    if code == 0:data1="01"
    elif code == 1 or code == 2:data1="02"
    elif code == 3:data1="03"
    elif code == 49:data1="50"
    elif code == 59:data1="09"
    elif code == 69 or code == 84:data1="10"
    elif code == 79 or code == 94:data1="13"
    elif code == 59:data1="09"
    elif code == 99:data1="11"

    return f"https://openweathermap.org/img/wn/{data1}{daytime}@4x.png"

def text_code(code):
    if code == 0:return '快晴'
    elif code == 1: return '晴れ'
    elif code == 2: return '一部雲'
    elif code == 3: return '曇り'
    elif code == 49: return '霧'
    elif code == 59: return '霧雨'
    elif code == 69: return '雨'
    elif code == 79: return '雪'
    elif code == 84: return 'にわか雨'
    elif code == 94: return '雪・雹'
    elif code == 99: return '雷雨'
    else: return '不明'


now_time=int(datetime.datetime.now().strftime("%H"))
print(now_time)
now_daytime = None
if(now_time < 6 or now_time > 17):
    now_daytime="n"
    print("Time is night")
else:
    now_daytime="d"
    print("Time is day")

response = requests.get(url=url)

print(response.text)
print("\n")
print(response.headers)

json_res=response.json()
print(type(json_res))


print(f"現在の気温は{json_res["current"]["temperature_2m"]}{json_res["current_units"]["temperature_2m"]}です。")
print(f"降水量は{json_res["current"]["precipitation"]}{json_res["current_units"]["precipitation"]}です。")
print(f"風速は{json_res["current"]["wind_speed_10m"]}{json_res["current_units"]["wind_speed_10m"]}です。")


saisho = None
if now_daytime == "n": saisho=  "こんばんは"
if now_daytime == "d": saisho=  "おはようございます"

outtext1 = f"""\
# 天気予報
みなさん{saisho}。
今日の天気は{text_code(json_res["current"]["weather_code"])}で、
予想最高気温は{json_res["daily"]["temperature_2m_max"][0]}{json_res["daily_units"]["temperature_2m_max"]}で、
予想最低気温は{json_res["daily"]["temperature_2m_min"][0]}{json_res["daily_units"]["temperature_2m_min"]}です。

４日間の天気
<t:{math.floor(datetime.datetime.strptime(json_res["daily"]["time"][1],'%Y-%m-%d').timestamp())}:R> : {json_res["daily"]["temperature_2m_max"][1]}{json_res["daily_units"]["temperature_2m_max"]} / {json_res["daily"]["temperature_2m_min"][1]}{json_res["daily_units"]["temperature_2m_min"]}
<t:{math.floor(datetime.datetime.strptime(json_res["daily"]["time"][2],'%Y-%m-%d').timestamp())}:R> : {json_res["daily"]["temperature_2m_max"][2]}{json_res["daily_units"]["temperature_2m_max"]} / {json_res["daily"]["temperature_2m_min"][2]}{json_res["daily_units"]["temperature_2m_min"]}
<t:{math.floor(datetime.datetime.strptime(json_res["daily"]["time"][3],'%Y-%m-%d').timestamp())}:R> : {json_res["daily"]["temperature_2m_max"][3]}{json_res["daily_units"]["temperature_2m_max"]} / {json_res["daily"]["temperature_2m_min"][3]}{json_res["daily_units"]["temperature_2m_min"]}
<t:{math.floor(datetime.datetime.strptime(json_res["daily"]["time"][4],'%Y-%m-%d').timestamp())}:R> : {json_res["daily"]["temperature_2m_max"][4]}{json_res["daily_units"]["temperature_2m_max"]} / {json_res["daily"]["temperature_2m_min"][4]}{json_res["daily_units"]["temperature_2m_min"]}
"""

print("\n"+outtext1)

print(f"{getenv("TENKI")}?content={outtext1}&avatar={images(json_res["current"]["weather_code"],now_daytime)}&name={text_code(json_res["current"]["weather_code"])}")
#discord = requests.get(
#    f"{getenv("TENKI")}?content={outtext1}&avatar={images(json_res["current"]["weather_code"],now_daytime)}&name={text_code(json_res["current"]["weather_code"])}",
#    headers = {'Content-Type': 'application/json'}
#)
#print()
#print(discord.status_code)
#print(discord.json())

url2="https://api.whatistoday.cyou/v2/anniv/"
now_time2=int(datetime.date.today().strftime("%m%d"))

response2 = requests.get(url=f"{url2}{now_time2}")
print()
print(response2.json())

nannnohi1=response2.json()["_items"][0]["anniv1"]
if(response2.json()["_items"][0]["anniv2"]!=""): nannnohi1=nannnohi1+response2.json()["_items"][0]["anniv2"]+"、"
if(response2.json()["_items"][0]["anniv3"]!=""): nannnohi1=nannnohi1+response2.json()["_items"][0]["anniv3"]+"、"
if(response2.json()["_items"][0]["anniv4"]!=""): nannnohi1=nannnohi1+response2.json()["_items"][0]["anniv4"]+"、"
if(response2.json()["_items"][0]["anniv5"]!=""): nannnohi1=nannnohi1+response2.json()["_items"][0]["anniv5"]+"、"

outtext2 = f"""\
今日は、{nannnohi1}です。
"""

async def webhook():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(getenv("TENKI"), session=session)
        await webhook.send(outtext1,username="天気予報",avatar_url=images(json_res["current"]["weather_code"],now_daytime))
        #コード
loop=asyncio.get_event_loop()
loop.run_until_complete(webhook())

async def webhook2():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(getenv("NANN"), session=session)
        await webhook.send(outtext2,username="今日は何の日BOT")
        #コード
loop2=asyncio.get_event_loop()
loop2.run_until_complete(webhook2())