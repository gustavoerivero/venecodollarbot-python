import requests
from os import getenv
from dotenv import load_dotenv


def set_webhook() -> None:
    try:

      load_dotenv()

      token = getenv("TOKEN") if getenv("TOKEN") else ""
      vercel = getenv("VERCEL") if getenv("VERCEL") else ""

      url = f"https://api.telegram.org/bot{token}/setWebhook"
      data = {"url": vercel}

      response = requests.post(url, json=data)
      print(f"Webhook setting: {response.json}")

    except Exception as ex:
       print(f"Set Webhook error: {ex}")