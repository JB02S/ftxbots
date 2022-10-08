import json
import os
import sys
import threading

import websocket
from dotenv import load_dotenv

from bots.bots import *
from ftx.rest.client import FtxClient

"""
Setting up client api, logging config, and websocket
"""

load_dotenv()

api_key = os.getenv('api_key_main')
api_secret = os.getenv('api_secret_main')

client = FtxClient(api_key=api_key, api_secret=api_secret)

if sys.platform.startswith('win'):
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '\\bots\\' + 'bot.log'
else:
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '/bots/' + 'bot.log'

logging.basicConfig(filename=logfile_path, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')


bot1 = Bot1(api_key, api_secret)
bot2 = Bot2(api_key, api_secret)

bot_arr = [bot1, bot2]


def live_trade_price_data(client: FtxClient):
    logging.info('bot starting live price data thread')

    while True:
        pass


def start_price_data_thread():
    threading.Thread(target=live_trade_price_data(client=client)).start()


def start_bots():
    for bots in bot_arr:
        bots.start_bot()


def handle_webhook_data(data: str):
    data_arr = data.split()
    data_arr[1] = data_arr[1][:-4]
    data_arr[3] = int(data_arr[3])
    for bots in bot_arr:
        if bots.to_string() == data_arr[0]:
            data_arr.pop(0)
            bots.update(data_arr)


start_bots()
