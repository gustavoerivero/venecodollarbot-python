import logging
import datetime
import pytz

from dateutil import parser

from telegram import Update

from telegram.ext import filters, Updater, CommandHandler, MessageHandler, CallbackContext, PrefixHandler

import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

base_url = "https://venecodollar.vercel.app/api/v1"
token = "6228195632:AAHY392ai11JzcQG9ID-485vrqmCpf_3HW4"

menu = """
*Comandos disponibles:*
/start - Entabla comunicación conmigo.
/help - Conoce los comandos disponibles.
/dolar - Obtener valores del dólar.
/fuente <nombre> - Obtener valores de una fuente específica.
/avisos - Activar los avisos de cambio de dólar.
/remover - Remover los avisos de cambio de dólar.
"""

welcome = f"¡Hola! A continuación te muestro las cosas que puedo hacer:\n{menu}\nAsí que dime, ¿qué puedo hacer por ti?"


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text=welcome,
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text=menu,
        parse_mode='Markdown'
    )


def dollar(update: Update, context: CallbackContext) -> None:
    url = f"{base_url}/dollar"
    response = requests.get(url)
    data = response.json()
    message = "*Valores del dólar:*\n"
    for entity in data["Data"]["entities"]:
        name = str(entity["info"]["title"]).split('@')
        title = ""
        if name[0] == "":
            title = name[1]
        else:
            title = name[0]
        dollar = entity["info"]["dollar"]
        updated_date = entity["info"]["updatedDate"]
        if dollar > 0:
            message += f"\n- *{title}* -\nDólar: Bs. {dollar}\nFecha de actualización: {updated_date}\n"
    average = data["Data"]["average"]
    message += f"\n*Promedio general:* Bs. {average}\n"

    update.message.reply_text(
        text=message,
        parse_mode='Markdown'
    )


def entity(update: Update, context: CallbackContext) -> None:

    try:

        entity_name = update.message.text.split()[1]
        url = f"{base_url}/dollar/entity?name={entity_name}"
        response = requests.get(url)
        data = response.json()

        message = f"*Valores del dólar para la entidad '{entity_name}':*\n"

        entities = data["Data"].get("entities")

        if entities:
            for entity in data["Data"]["entities"]:
                name = str(entity["info"]["title"]).split('@')
                title = ""
                if name[0] == "":
                    title = name[1]
                else:
                    title = name[0]
                dollar = entity["info"]["dollar"]
                updated_date = entity["info"]["updatedDate"]
                if dollar > 0:
                    message += f"\n- {title} -\nDólar: Bs. {dollar}\nFecha de actualización: {updated_date}\n"
        else:
            title = data["Data"]["info"]["title"]
            dollar = data["Data"]["info"]["dollar"]
            updated_date = data["Data"]["info"]["updatedDate"]
            message += f"\n- *{title}* -\nDólar: Bs. {dollar}\nFecha de actualización: {updated_date}\n"

        average = data["Data"].get("average")

        if average:
            message += f"\n*Promedio general:* Bs. {average}\n"

        update.message.reply_text(
            text=message,
            parse_mode='Markdown'
        )

    except Exception:
        message = "Debes proporcionar un nombre correcto para la fuente monitora del dólar."
        update.message.reply_text(
            text=message,
            parse_mode='Markdown'
        )


def unknown_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text
    update.message.reply_text(
        text=f"El comando '{command}' es desconocido. Por favor, utiliza los comandos disponibles.\n\nSi deseas conocer los comandos disponibles, utiliza /help.",
        parse_mode='Markdown'
    )


def daily_alarm(context: CallbackContext) -> None:
    url = f"{base_url}/dollar"
    response = requests.get(url)
    data = response.json()
    date = data["Data"]["date"].split('T')
    venezuela_time = convert_venezuela_utc(date[1])
    message = f"*Valores del dólar {venezuela_time}:*\n"
    for entity in data["Data"]["entities"]:
        name = str(entity["info"]["title"]).split('@')
        title = ""
        if name[0] == "":
            title = name[1]
        else:
            title = name[0]
        dollar = entity["info"]["dollar"]
        updated_date = entity["info"]["updatedDate"]
        if dollar > 0:
            message += f"\n- *{title}* -\nDólar: Bs. {dollar}\nFecha de actualización: {updated_date}\n"
    average = data["Data"]["average"]
    message += f"\n*Promedio general:* Bs. {average}\n"

    context.bot.send_message(
        chat_id=context.job.context,
        text=message,
        parse_mode='Markdown'
    )


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_message.chat_id
    try:

        job_removed = remove_job_if_exists(str(chat_id), context)

        tz = pytz.timezone('America/Caracas')
        morning_time = datetime.time(
            hour=9,
            minute=0,
            second=0,
            tzinfo=tz
        )

        afternoon_time = datetime.time(
            hour=13,
            minute=0,
            second=0,
            tzinfo=tz
        )

        context.job_queue.run_daily(
            daily_alarm,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=morning_time,
            context=chat_id
        )

        context.job_queue.run_daily(
            daily_alarm,
            days=(0, 1, 2, 3, 4, 5, 6),
            time=afternoon_time,
            context=chat_id
        )

        text = "¡Los avisos de cambio de dólar han sido activados exitosamente!"
        if job_removed:
            text += " Asimismo, los viejos avisos fueron removidos."
        update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        update.effective_message.reply_text("Utiliza el comando /avisos")


def unset(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "¡Los avisos fueron removidos exitosamente!" if job_removed else "No tienes avisos activos."
    update.message.reply_text(text)


def convert_venezuela_utc(time: str) -> str | None:
    try:
        utc_time = parser.parse(time)

        utc_timezone = pytz.timezone("UTC")
        utc_time = utc_time.replace(tzinfo=utc_timezone)

        venezuela_timezone = pytz.timezone("America/Caracas")
        venezuela_time = utc_time.astimezone(venezuela_timezone)

        venezuela_time_str = venezuela_time.strftime("%I:%M %p")

        return venezuela_time_str

    except (parser.ParserError, pytz.UnknownTimeZoneError, ValueError):
        return None


def main() -> None:
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


if __name__ == '__main__':
    main()
