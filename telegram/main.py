#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import telegram
from telegram.constants import ChatAction
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from agents import Agent, Runner, SQLiteSession

agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

sessions = {}

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    chat_id = update.effective_chat.id
    session_id = f"chat_{chat_id}"
    session = SQLiteSession(session_id, "bot.sql")

    await update.message.reply_chat_action(ChatAction.TYPING)

    result = await Runner.run(
        agent,
        update.message.text,
        session=session
    )
    await update.message.reply_text(result.final_output)


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()