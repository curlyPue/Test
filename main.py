"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
"""

import logging
from typing import Tuple, Optional
from telegram import (
  Chat,
  ChatMember,
  ChatMemberUpdated,
  ForceReply,
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  ParseMode,
  Update
)
from telegram.ext import (
  CallbackContext,
  CallbackQueryHandler,
  ChatMemberHandler,
  CommandHandler,
  Filters,
  MessageHandler,
  Updater
)

# Enable logging
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

greetings = 'Привет! Это чат медицинских технологов, мы здесь знакомимся и обсуждаем насущные проблемы. Пожалуйста, не стесняйся задавать волнующие тебя вопросы, коллеги с радостью помогут. Кстати, мы здесь друг к другу на "ты", поверь, это реально сближает🤗. Пожалуйста, прочитай закреплённое сообщение с правилами чата. Если откроешь чат <a href="https://t.me/TehnologichniyBot">со мной</a>, то смогу тебе быстро давать всякую полезную инфу. А если тебе интересно информационное моделирование, то присоединяйся ещё и к <a href="https://t.me/joinchat/WM9qX88NvFa9b06W">этому</a> чату.'

# Define a few command handlers. These usually take the two arguments update and context.
def start_command(update: Update, context: CallbackContext) -> None:
  """Sends a message with three inline buttons attached."""
  userName = update.message.from_user.first_name
  answer = 'Привет, ' + userName + '! Я вроде дворецкого в чате медицинских технологов, а в личке могу напоминать о разных полезных вещах. Я пока ещё довольно тупенький, но @curlyPue надо мной работает. Если у тебя есть предложения как сделать меня полезнее - пиши ему скорей! Вызвать меню с ништяками можно командой /menu или нажав на синюю кнопку слева от строки ввода текста🙂'
  
  keyboard = [
    [
      InlineKeyboardButton("Ты кто?", callback_data='1'),
      InlineKeyboardButton("Option 2", callback_data='2'),
    ],
    [InlineKeyboardButton("Option 3", callback_data='3')],
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text(answer, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
  """Parses the CallbackQuery and updates the message text."""
  query = update.callback_query

  # CallbackQueries need to be answered, even if no notification to the user is needed
  # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
  query.answer()

  query.edit_message_text(text=f"Вы выбрали: {query.data}")

def help_command(update: Update, context: CallbackContext) -> None:
  """Send a message when the command /help is issued."""
  update.message.reply_text('Помогите!')


def message(update: Update, context: CallbackContext) -> None:
  answer = 'answer'                                                     #что-то придумать
  update.message.reply_text(answer)

def main() -> None:
  """Start the bot."""
  # Create the Updater and pass it your bot's token.
  updater = Updater("6256486251:AAHKx9OIMG6Q9g98p6XH8tzBuFmQSwrIt8M")

  # Get the dispatcher to register handlers
  dispatcher = updater.dispatcher

  dispatcher.add_handler(CommandHandler("start", start_command))
  dispatcher.add_handler(CommandHandler("help", help_command))
  dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message))
  updater.dispatcher.add_handler(CallbackQueryHandler(button))

  # Start the Bot
  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()


"""
# echo function
def echo(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(update.message.text)
"""
