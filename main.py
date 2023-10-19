import pytz
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from config import TOKEN
import handlers
from database import *
from models import *
from apscheduler.schedulers.background import BackgroundScheduler


def send_updates(updater):
    current_rate = handlers.get_current_rate()
    session = Session()
    subscribed_users = session.query(User).filter_by(is_subscribed=True).all()

    for user in subscribed_users:
        updater.bot.send_message(chat_id=str(user.chat_id), text=f"Текущий курс доллара: {current_rate} ")


updater = Updater(token=TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", handlers.start))
dp.add_handler(CommandHandler("rate", handlers.rate))
dp.add_handler(CommandHandler("subscribe", handlers.subscribe))
dp.add_handler(CommandHandler("unsubscribe", handlers.unsubscribe))
dp.add_handler(CommandHandler("history", handlers.history))
dp.add_handler(CallbackQueryHandler(handlers.button))
tz = pytz.timezone('Europe/Moscow')
scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(send_updates, 'cron', hour='9,18', minute=0, second=0, args=[updater])
scheduler.start()

if __name__ == '__main__':
    updater.start_polling(timeout=123)
