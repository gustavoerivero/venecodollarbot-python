import pytz
import datetime

from telegram import Update
from telegram.ext import CallbackContext

from src.api import get_dollar, get_entities
from src.jobs import remove_job_if_exists, daily_alarm
from src.utils import timezone

menu = """
*Comandos disponibles:*
/start - Entabla comunicación conmigo.
/help - Conoce los comandos disponibles.
/dolar - Obtener valores del dólar.
/fuente <nombre> - Obtener valores de una fuente específica.
/avisos - Activar los avisos de cambio de dólar.
/remover - Remover los avisos de cambio de dólar.
"""


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text=f"¡Hola! A continuación te muestro las cosas que puedo hacer:\n{menu}\nAsí que dime, ¿qué puedo hacer por ti?",
        parse_mode='Markdown'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text=menu,
        parse_mode='Markdown'
    )


def dollar(update: Update, context: CallbackContext) -> None:
    try:
        data = get_dollar()
        message = "*Valores del dólar:*\n"
        for entity in data["Data"]["entities"]:
            name = str(entity["info"]["title"]).split('@')
            title = name[1] if name[0] == "" else name[0]
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
    except Exception as ex:
        print(f"Dollar command error: {ex}")


def entity(update: Update, context: CallbackContext) -> None:
    try:
        entity_name = update.message.text.split()[1]
        data = get_entities(entity=entity_name)
        message = f"*Valores del dólar para la entidad '{entity_name}':*\n"
        entities = data["Data"].get("entities")
        if entities:
            for entity in data["Data"]["entities"]:
                name = str(entity["info"]["title"]).split('@')
                title = name[1] if name[0] == "" else name[0]
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

    except Exception as ex:
        print(f"Entity command error: {ex}")
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


def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        tz = pytz.timezone(timezone)
        morning_time = datetime.time(hour=9, minute=0, second=0, tzinfo=tz)
        afternoon_time = datetime.time(hour=13, minute=0, second=0, tzinfo=tz)
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
    try:
        chat_id = update.message.chat_id
        job_removed = remove_job_if_exists(str(chat_id), context)
        text = "¡Los avisos fueron removidos exitosamente!" if job_removed else "No tienes avisos activos."
        update.message.reply_text(text)
    except Exception as ex:
        print(f"Unset timer command error: {ex}")
