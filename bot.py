import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import redis
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


def get_redis_host():
    if os.getenv("INSIDE_DOCKER"):
        return "redis"
    return "localhost"


async def main():
    load_dotenv()

    API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
    REDIS_HOST = get_redis_host()
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    logging.info(f"Using Redis host: {REDIS_HOST}")

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    @dp.message(Command(commands=['exchange']))
    async def exchange(message: types.Message):
        try:
            logging.info(f"Получено сообщение: {message.text}")
            _, from_currency, to_currency, amount = message.text.split()
            logging.info(
                f"Разобранные значения - from_currency: {from_currency}, to_currency: {to_currency}, amount: {amount}")

            from_rate = r.get(from_currency)
            to_rate = r.get(to_currency)
            if from_rate is None or to_rate is None:
                raise ValueError("Валюта не найдена в базе данных")

            from_rate = float(from_rate)
            to_rate = float(to_rate)
            amount = float(amount)
            result = (amount * from_rate) / to_rate
            await message.reply(f"{amount} {from_currency} = {result:.2f} {to_currency}")
        except ValueError as ve:
            logging.error(f"Ошибка: {ve}")
            await message.reply("Ошибка: Валюта не найдена в базе данных.")
        except Exception as e:
            logging.error(f"Ошибка при обработке команды: {e}")
            await message.reply("Ошибка при обработке команды. Проверьте правильность ввода.")

    @dp.message(Command(commands=['rates']))
    async def rates(message: types.Message):
        try:
            logging.info(f"Получено сообщение: {message.text}")
            keys = r.keys()
            rates = {key.decode('utf-8'): float(r.get(key)) for key in keys}
            rates_str = '\n'.join([f"{k}: {v}" for k, v in rates.items()])
            await message.reply(f"Актуальные курсы валют:\n{rates_str}")
        except Exception as e:
            logging.error(f"Ошибка при обработке команды: {e}")
            await message.reply("Ошибка при обработке команды.")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
