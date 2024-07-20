import logging
from aiogram import Bot, Dispatcher, executor, types
import redis
import os

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    try:
        _, from_currency, to_currency, amount = message.text.split()
        from_rate = float(r.get(from_currency))
        to_rate = float(r.get(to_currency))
        amount = float(amount)
        result = (amount * from_rate) / to_rate
        await message.reply(f"{amount} {from_currency} = {result:.2f} {to_currency}")
    except Exception as e:
        await message.reply("Ошибка при обработке команды. Проверьте правильность ввода.")


@dp.message_handler(commands=['rates'])
async def rates(message: types.Message):
    try:
        keys = r.keys()
        rates = {key.decode('utf-8'): float(r.get(key)) for key in keys}
        rates_str = '\n'.join([f"{k}: {v}" for k, v in rates.items()])
        await message.reply(f"Актуальные курсы валют:\n{rates_str}")
    except Exception as e:
        await message.reply("Ошибка при обработке команды.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
