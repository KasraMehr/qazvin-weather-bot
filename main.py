import datetime
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Environment Variables ---

TOKEN = "8277037293:AAEk626y-PfJBeXG0659wzVtkahkWPLb-tE"
OPENWEATHER_API_KEY = "1ad15b7bd719ebaf6faa8770a203f089"

CITY = "Qazvin"
PORT = int(os.environ.get("PORT", 5000))  # Render uses this

# --- Flask App ---
flask_app = Flask(__name__)

# --- Telegram App ---
application = Application.builder().token(TOKEN).build()

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋 من هر روز ساعت ۷ صبح بهت می‌گم چی بپوشی ☀️\n"
        "برای شروع، دستور /register رو بفرست ✅"
    )

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users = context.bot_data.setdefault("users", set())
    users.add(chat_id)
    await update.message.reply_text("ثبت شد ✅ از فردا ساعت ۷ صبح پیام برات می‌فرستم 🌤️")

# --- Get weather ---
def get_avg_temperature():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&units=metric&appid={OPENWEATHER_API_KEY}"
    data = requests.get(url).json()

    temps = []
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3.5)
    today = now.date()

    for item in data["list"]:
        dt = datetime.datetime.utcfromtimestamp(item["dt"]) + datetime.timedelta(hours=3.5)
        if dt.date() == today and 8 <= dt.hour <= 17:
            temps.append(item["main"]["temp"])

    if temps:
        return sum(temps) / len(temps)
    return None

# --- Daily message ---
async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    avg_temp = get_avg_temperature()
    if avg_temp is None:
        msg = "نتونستم دمای امروز رو پیدا کنم 😅"
    elif avg_temp < 5:
        msg = "خیلی سرده! کاپشن ضخیم یادت نره 🧥"
    elif avg_temp < 15:
        msg = "هوا خنکه، سویشرت خوبه 😌"
    elif avg_temp < 25:
        msg = "هوا معتدله، لباس راحت بپوش 😎"
    elif avg_temp < 35:
        msg = "هوا گرمه، لباس نخی بپوش ☀️"
    else:
        msg = "خیلی گرمه، تا می‌تونی خنک بمون 😰"

    for chat_id in context.application.bot_data.get("users", set()):
        await context.bot.send_message(chat_id, f"دمای میانگین امروز قزوین: {avg_temp:.1f}°C\n{msg}")

# --- Add Handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("register", register_user))

# --- Job (7 AM Tehran) ---
tehran_time = datetime.time(hour=7, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3, minutes=30)))
application.job_queue.run_daily(send_daily_weather, time=tehran_time)

# --- Flask route for Telegram Webhook ---
@flask_app.route("/" + TOKEN, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# --- Root test route ---
@flask_app.route("/")
def index():
    return "Bot is running!"

# --- Main Entry ---
if __name__ == "__main__":
    print("Starting bot with Webhook...")
    # وقتی Render آدرس HTTPS بده، باید اون رو ست کنیم:
    WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )

    flask_app.run(host="0.0.0.0", port=PORT)
