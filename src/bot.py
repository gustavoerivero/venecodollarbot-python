import requests

from telegram.ext import Updater, CommandHandler, PrefixHandler, MessageHandler, filters
from os import getenv
from dotenv import load_dotenv

from src.commands import start, dollar, entity, set_timer, unset, help_command, unknown_command
from src.webhook import set_webhook

def bot() -> None:

    try:

        set_webhook()

        load_dotenv()

        token = getenv("TOKEN") if getenv("TOKEN") else ""

        updater = Updater(token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(PrefixHandler(
            ['/', '!', 'help'], ['start', 'start@venecodollarbot'], start))

        dispatcher.add_handler(CommandHandler('dolar', dollar))
        dispatcher.add_handler(CommandHandler('fuente', entity))
        dispatcher.add_handler(CommandHandler('avisos', set_timer))
        dispatcher.add_handler(CommandHandler('remover', unset))
        dispatcher.add_handler(CommandHandler('help', help_command))

        dispatcher.add_handler(MessageHandler(
            filters.Filters.command | ~filters.Filters.command, unknown_command))

        updater.start_polling()
        updater.idle()

    except Exception as ex:
        print(f"Build bot error: {ex}")
