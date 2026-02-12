import os
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")
import urllib, requests
url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (
    f'{TELEGRAM_BOT_TOKEN}', f'{CHAT_ID}', urllib.parse.quote_plus('<message>'))
_ = requests.get(url, timeout=10)