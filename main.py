import os
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")  # توی Render مقدار بده
CHAT_ID = os.environ.get("CHAT_ID")  # آیدی خودت

CITY = "Qazvin"
API_KEY = "b6907d289e10d714a6e88b30761fae22"  # OpenWeatherMap test key

async def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    temp = data["main"]["temp"]
    return f"🌤️ دمای فعلی {CITY}: {temp}°C"

async def send_weather(application):
    weather = await get_weather()
    await application.bot.send_message(chat_id=CHAT_ID, text=weather)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من هر روز ساعت ۸ صبح دمای قزوین رو می‌فرستم 🌞")

async def schedule_weather(application):
    while True:
        now = asyncio.get_event_loop().time()
        target_hour = 4.5
        seconds_in_day = 24 * 60 * 60
        delay = (target_hour * 3600 - (now % seconds_in_day)) % seconds_in_day
        await asyncio.sleep(delay)
        await send_weather(application)
        await asyncio.sleep(24 * 3600)  # روز بعد

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # تسک ارسال روزانه بدون JobQueue
    asyncio.create_task(schedule_weather(application))

    print("✅ Bot started successfully")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
