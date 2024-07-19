import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


async def fetch_currency_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(CBR_URL) as response:
            if response.status == 200:
                data = await response.text()
                return data
            else:
                print("Failed to fetch data")
                return None


def parse_and_update_rates(xml_data):
    root = ET.fromstring(xml_data)
    for currency in root.findall('Valute'):
        char_code = currency.find('CharCode').text
        value = currency.find('Value').text.replace(',', '.')
        r.set(char_code, float(value))


async def update_currency_rates():
    xml_data = await fetch_currency_rates()
    if xml_data:
        parse_and_update_rates(xml_data)


if __name__ == "__main__":
    asyncio.run(update_currency_rates())
