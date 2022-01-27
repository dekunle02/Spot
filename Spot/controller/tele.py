import os
from dotenv import load_dotenv

from telegram import Bot,Update, File
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from database import fire
from . import replies

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']


def help_command_handler(update: Update, context: CallbackContext):
    update.message.reply_text(text=replies.HELP_MESSAGE)


def setup_command_handler(update: Update, context: CallbackContext):
    
    pass
