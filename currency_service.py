import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import aioredis
import os
from decimal import Decimal
from dotenv import load_dotenv
from aiojobs import Scheduler

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


def parse_currency_data(xml_data):
    root = ET.fromstring(xml_data)
    currencies = {}
    for currency in root.findall("Valute"):
        char_code = currency.find("CharCode").text
        nominal = int(currency.find("Nominal").text)
        value = Decimal(currency.find("Value").text.replace(",", "."))
        unit_rate = value / nominal
        currencies[char_code] = str(unit_rate)
    return currencies


async def update_currency_rates(redis_url):
    xml_data = await fetch_currency_rates()
    if xml_data:
        currency_data = parse_currency_data(xml_data)
        redis = await aioredis.create_redis_pool(redis_url)
        try:
            async with redis.pipeline(transaction=True) as pipe:
                await pipe.mset_dict(currency_data).execute()
            print("Currency rates updated successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            redis.close()
            await redis.wait_closed()


async def scheduler(redis_url):
    scheduler = Scheduler()
    while True:
        await scheduler.spawn(update_currency_rates(redis_url))
        await asyncio.sleep(86400)


def main():
    load_dotenv()
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_db = os.getenv("REDIS_DB", "0")
    redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

    asyncio.run(scheduler(redis_url))


if __name__ == "__main__":
    main()
