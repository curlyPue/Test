import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import (
  Chat,
  ChatMember,
  ChatMemberUpdated,
  ForceReply,
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  Update
)
from telegram.constants import ParseMode
from telegram.ext import (
  Application,
  CallbackQueryHandler,
  ChatMemberHandler,
  CommandHandler,
  ContextTypes,
  MessageHandler,
  filters
)
from typing import Optional, Tuple
from auth_data import token

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /start is issued."""
  chat = update.effective_chat
  if chat.type == Chat.PRIVATE:
    user = update.effective_user
    await update.message.reply_html(
      rf"Привет, {user.mention_html()}! Я вроде дворецкого в чате медицинских технологов, а в личке могу напоминать о разных полезных вещах. Я пока ещё довольно тупенький, но @curlyPue надо мной работает. Если у тебя есть предложения как сделать меня полезнее - пиши ему скорей! Вызвать меню с ништяками можно командой /menu или нажав на синюю кнопку слева от строки ввода текста🙂",
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /menu is issued."""
  chat = update.effective_chat
  if chat.type == Chat.PRIVATE:
    keyboard = [
        [
          InlineKeyboardButton("Техдоки на оборудование", callback_data="https://disk.yandex.ru/d/3BA7ALfoYSyM9Q"),
        ],
        [ 
          InlineKeyboardButton("Порядки оказания медицинской помощи", callback_data="https://clck.ru/33hvpE"),
        ],
        [
          InlineKeyboardButton("Литература", callback_data="https://disk.yandex.ru/d/0NEmEAbgkk3x9w")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Привет! Чем могу помочь?", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"{query.data}")


#async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #"""Send message to the user."""
    #await update.message.reply_text(update.message.text)

#async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #"""Send message to the user."""
    #await update.message.reply_text(update.message.text)

def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            logger.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    else:
        if not was_member and is_member:
            logger.info("%s added the bot to the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
            context.bot_data.setdefault("channel_ids", set()).discard(chat.id)


async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows which chats the bot is in"""
    user_ids = ", ".join(str(uid) for uid in context.bot_data.setdefault("user_ids", set()))
    group_ids = ", ".join(str(gid) for gid in context.bot_data.setdefault("group_ids", set()))
    channel_ids = ", ".join(str(cid) for cid in context.bot_data.setdefault("channel_ids", set()))
    text = (
        f"@{context.bot.username} is currently in a conversation with the user IDs {user_ids}."
        f" Moreover it is a member of the groups with IDs {group_ids} "
        f"and administrator in the channels with IDs {channel_ids}."
    )
    await update.effective_message.reply_text(text)


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()

    if not was_member and is_member:
        await update.effective_chat.send_message(
            f'Привет, {member_name}! Это чат медицинских технологов, мы здесь знакомимся и обсуждаем насущные проблемы. Пожалуйста, не стесняйся задавать волнующие тебя вопросы, коллеги с радостью помогут. Кстати, мы здесь друг к другу на "ты", поверь, это реально сближает🤗. Пожалуйста, прочитай закреплённое сообщение с правилами чата. Если откроешь чат <a href="https://t.me/TehnologichniyBot">со мной</a>, то смогу тебе быстро давать всякую полезную инфу. А если тебе интересно информационное моделирование, то присоединяйся ещё и к <a href="https://t.me/+KTZ5vAWYB0U4YWZi">этому</a> чату.',
            parse_mode=ParseMode.HTML,
        )
    elif was_member and not is_member:
        await update.effective_chat.send_message(
            f"{member_name} больше не с нами😥",
            parse_mode=ParseMode.HTML,
        )


async def start_private_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Records that user started a chat with the bot if it's a private chat.
    Since no `my_chat_member` update is issued when a user starts a private chat with the bot
    for the first time, we have to track it explicitly here.
    """
    user_name = update.effective_user.full_name
    chat = update.effective_chat
    if chat.type != Chat.PRIVATE or chat.id in context.bot_data.get("user_ids", set()):
        return

    logger.info("%s started a private chat with the bot", user_name)
    context.bot_data.setdefault("user_ids", set()).add(chat.id)

    #await update.effective_message.reply_text(
        #f"Welcome {user_name}. Use /show_chats to see what chats I'm in."
    #)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))

    # on non command i.e message - reply to the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    # Keep track of which chats the bot is in
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("show_chats", show_chats))

    # Handle members joining/leaving chats.
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    # Interpret any other command or text message as a start of a private chat.
    # This will record the user as being in a private chat with bot.
    application.add_handler(MessageHandler(filters.ALL, start_private_chat))

    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
