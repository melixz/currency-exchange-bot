import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import redis
import os
from dotenv import load_dotenv

CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


async def fetch_currency_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(CBR_URL) as response:
            if response.status == 200:
                data = await response.text()
                return data
            else:
                print("Failed to fetch data")
                return None


def parse_and_update_rates(redis_client, xml_data):
    root = ET.fromstring(xml_data)
    for currency in root.findall('Valute'):
        char_code = currency.find('CharCode').text
        value = currency.find('Value').text.replace(',', '.')
        redis_client.set(char_code, float(value))


async def update_currency_rates():
    xml_data = await fetch_currency_rates()
    if xml_data:
        parse_and_update_rates(r, xml_data)


def main():
    load_dotenv()
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))

    global r
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    asyncio.run(update_currency_rates())


if __name__ == "__main__":
    main()
