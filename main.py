from WordChainBot import WordChainBot
from dotenv import load_dotenv
import os
import logging.handlers

load_dotenv()
token = os.environ["TOKEN"]
bot = WordChainBot()

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(filename="discord.log", encoding="utf-8", maxBytes=32 * 1024 * 1024, backupCount=5)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

bot.run(token=token, log_handler=None)
