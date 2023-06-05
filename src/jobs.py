from telegram.ext import CallbackContext

from src.api import get_dollar
from src.utils import convert_venezuela_utc


def daily_alarm(context: CallbackContext) -> None:
    try:
        data = get_dollar()
        date = data["Data"]["date"].split('T')
        venezuela_time = convert_venezuela_utc(date[1])
        message = f"*Valores del dólar {venezuela_time}:*\n"
        for entity in data["Data"]["entities"]:
            name = str(entity["info"]["title"]).split('@')
            title = name[1] if name[0] == "" else name[0]
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

    except Exception as ex:
        print(f"Daily alarm error: {ex}")
        return None


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
