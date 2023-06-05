import pytz

from dateutil import parser
from typing import Optional
from os import getenv
from dotenv import load_dotenv

load_dotenv()

timezone = getenv("TIMEZONE") if getenv("TIMEZONE") else ""


def convert_venezuela_utc(time: str) -> Optional[str]:
    try:
        utc_time = parser.parse(time)
        utc_timezone = pytz.timezone("UTC")
        utc_time = utc_time.replace(tzinfo=utc_timezone)
        venezuela_timezone = pytz.timezone(timezone)
        venezuela_time = utc_time.astimezone(venezuela_timezone)
        venezuela_time_str = venezuela_time.strftime("%I:%M %p")
        return venezuela_time_str
    except (parser.ParserError, pytz.UnknownTimeZoneError, ValueError):
        return None
