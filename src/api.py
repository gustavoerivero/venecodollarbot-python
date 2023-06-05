import requests
from requests import Response

from os import getenv
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

base_url = getenv("API_URL") if getenv("API_URL") else ""


def get_dollar() -> Optional[Response.json]:
    try:
        response = requests.get(f"{base_url}/dollar")
        data = response.json()
        return data
    except Exception as ex:
        print(f"Dollar request error: {ex}")
        return None


def get_entities(entity: str) -> Optional[Response.json]:
    try:
        response = requests.get(f"{base_url}/dollar/entity?name={entity}")
        data = response.json()
        return data
    except Exception as ex:
        print(f"Dollar request error: {ex}")
        return None
