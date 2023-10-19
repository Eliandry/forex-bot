from telegram import Update
from telegram.ext import CallbackContext
from database import Session
from models import User, RateHistory
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
def start(update: Update, context: CallbackContext) -> None:
    session=Session()
    user = session.query(User).filter_by(chat_id=str(update.message.chat_id)).first()
    if not user:
        user = User(chat_id=str(update.message.chat_id))
        session.add(user)
        session.commit()
        session.close()
    keyboard = [
        [InlineKeyboardButton("📈 Узнать курс доллара 📈", callback_data='rate')],
        [InlineKeyboardButton("🔔 Подписаться на обновления 🔔", callback_data='subscribe')],
        [InlineKeyboardButton("🔕 Отписаться от обновлений 🔕", callback_data='unsubscribe')],
        [InlineKeyboardButton("📜 Посмотреть историю запросов 📜", callback_data='history')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

def rate(update: Update, context: CallbackContext,chat_id=None) -> None:
    session = Session()
    if not chat_id:
        chat_id = str(update.message.chat_id)
    current_rate = get_current_rate()
    user = session.query(User).filter_by(chat_id=str(chat_id)).first()
    rate_history = RateHistory(user_id=str(user.id), rate=current_rate)
    session.add(rate_history)
    session.commit()
    session.close()

    if not chat_id:
        update.message.reply_text(f'Курс на данный момент: {current_rate} руб.')
    else:
        update.callback_query.message.reply_text(f'Курс на данный момент: {current_rate} руб.')

def get_current_rate() -> float:
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

    return data['Valute']['USD']['Value']

def subscribe(update: Update, context: CallbackContext,chat_id=None) -> None:
    session = Session()
    if not chat_id:
        chat_id = str(update.message.chat_id)
    user = session.query(User).filter_by(chat_id=str(chat_id)).first()
    if user:
        user.is_subscribed = 1
        session.commit()
        session.close()
        if not chat_id:
            update.message.reply_text('Вы подписались на рассылку!')
        else:
            update.callback_query.message.reply_text('Вы подписались на рассылку!')
    else:
        if not chat_id:
            update.message.reply_text('Ошибка!')
        else:
            update.callback_query.message.reply_text('Вы подписались на рассылку!')

def unsubscribe(update: Update, context: CallbackContext,chat_id=None) -> None:
    session = Session()
    if not chat_id:
        chat_id = str(update.message.chat_id)
    user = session.query(User).filter_by(chat_id=str(chat_id)).first()
    if user:
        user.is_subscribed = 0
        session.commit()
        session.close()
        if not chat_id:
            update.message.reply_text('Вы больше не подписаны на рассылку((')
        else:
            update.callback_query.message.reply_text('Вы больше не подписаны на рассылку((')
    else:
        update.message.reply_text('Ошибка')


def history(update: Update, context: CallbackContext,chat_id=None):
    session = Session()
    if not chat_id:
        chat_id = str(update.message.chat_id)
    user = session.query(User).filter_by(chat_id=str(chat_id)).first()
    if not user:
        update.message.reply_text("Вы ещё не запрашивали курс доллара.")
        return

    if not user.rates:
        if not chat_id:
            update.message.reply_text("У вас нет истории запросов.")
        else:
            update.callback_query.message.reply_text("У вас нет истории запросов.")
        return

    history_text = "Ваша история курсов доллара:\n\n"
    for entry in user.rates[-15:]:
        history_text += f"{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {entry.rate} USD\n"
    session.close()
    if not chat_id:
        update.message.reply_text(history_text)
    else:
        update.callback_query.message.reply_text(history_text)

def button(update, context):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id

    if query.data == "rate":
        rate(update, context, chat_id=chat_id)
    elif query.data == "subscribe":
        subscribe(update, context, chat_id=chat_id)
    elif query.data == "unsubscribe":
        unsubscribe(update, context, chat_id=chat_id)
    elif query.data == "history":
        history(update, context, chat_id=chat_id)