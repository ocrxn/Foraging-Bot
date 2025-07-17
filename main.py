import asyncio
from bot_instance import bot
from config import *
from db import (update_db_loop,shutdown)
import logic
import signal
from view import create_view


def signal_handler(sig, frame):
    print(f"Signal received: {sig}")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown())

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

update_task = None
stop_event = asyncio.Event()

@bot.event
async def on_ready():
    try:
        global update_task
        print(f'{bot.user} has connected to Discord!')
        update_task = asyncio.create_task(update_db_loop())
    except Exception as e:
        print(f"Bot ran into an unexpected error during sync: {e}")

bot.run(TOKEN)