import os
import requests
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, Job

# --- Environment Variables ---
TOKEN = os.environ["8277037293:AAEk626y-PfJBeXG0659wzVtkahkWPLb-tE"]
OPENWEATHER_API_KEY = os.environ["1ad15b7bd719ebaf6faa8770a203f089"]

CITY = "Qazvin"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من هر روز ساعت ۷ صبح بهت میگم امروز تو قزوین چی بپوشی ☀️\n"
        "برای شروع، دستور /register رو بفرست ✅"
    )

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = context.bot_data.setdefault("users", set())
    users.add(chat_id)
    await update.message.reply_text("ثبت شد ✅ از فردا صبح ساعت ۷ پیام برات می‌فرستم 🌤️")

def get_avg_temperature():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&units=metric&appid={OPENWEATHER_API_KEY}"
    data = requests.get(url).json()

    temps = []
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3.5)  # تهران
    today = now.date()

    for item in data["list"]:
        dt = datetime.datetime.utcfromtimestamp(item["dt"]) + datetime.timedelta(hours=3.5)
        if dt.date() == today and 8 <= dt.hour <= 17:
            temps.append(item["main"]["temp"])

    if temps:
        return sum(temps) / len(temps)
    return None

async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    avg_temp = get_avg_temperature()

    if avg_temp is None:
        msg = "نتونستم دمای امروز قزوین رو پیدا کنم 😅"
    elif avg_temp < 5:
        msg = "خیلی سرده! کاپشن ضخیم، کلاه و دستکش یادت نره 🧥🧣"
    elif avg_temp < 15:
        msg = "هوا خنکه، یه ژاکت یا سویشرت خوبه 😌"
    elif avg_temp < 25:
        msg = "هوا معتدله، لباس راحت و نازک بپوش 😎"
    elif avg_temp < 35:
        msg = "هوا گرمه، لباس نخی و روشن بپوش ☀️"
    else:
        msg = "خیلی گرمه! بهتره تا می‌تونی خنک بمونی 😰"

    for chat_id in context.application.bot_data.get("users", set()):
        if avg_temp:
            text = f"دمای میانگین امروز قزوین: {avg_temp:.1f}°C\n{msg}"
        else:
            text = msg
        await context.bot.send_message(chat_id=chat_id, text=text)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register_user))

    tehran_time = datetime.time(hour=7, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3, minutes=30)))
    app.job_queue.run_daily(send_daily_weather, time=tehran_time)

    app.run_polling()

if __name__ == "__main__":
    main()
