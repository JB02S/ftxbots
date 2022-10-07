import datetime
import json
import logging
import os
import sys
import threading
import time

import pandas as pd
import websocket
from dotenv import load_dotenv

from bots.bot1 import Bot1
from bots.bot2 import Bot2
from ftx.rest.client import FtxClient

"""
Setting up client api, logging config, and websocket
"""

load_dotenv()

api_key = os.getenv('api_key_main')
api_secret = os.getenv('api_secret_main')

client = FtxClient(api_key=api_key, api_secret=api_secret)

if sys.platform.startswith('win'):
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '\\' + 'bot.log'
else:
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'bot.log'

logging.basicConfig(filename=logfile_path, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')

endpoint = 'wss://ftx.com/ws/'
our_msg = json.dumps({'op': 'subscribe', 'channel': 'ticker', 'market': 'BTC/USDT'})


def on_open(ws):
    ws.send(our_msg)


def on_message(ws, message):
    global out
    out = json.loads(message)


ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)

bot1 = Bot1(api_key, api_secret)
bot2 = Bot2(api_key, api_secret)

bot_arr = [bot1, bot2]

"""Using FTX REST API for making requests to the exchange, and using FTX Websocket API for live price data"""


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


def get_past_hour_historical_info(ftx_client: FtxClient, market: str):

    today_unix_timestamp = time.mktime(datetime.datetime.now().timetuple())
    hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    hour_ago_unix_timestamp = time.mktime(hour_ago.timetuple())

    historical = ftx_client.get_historical_prices(market=market, resolution=60, start_time=hour_ago_unix_timestamp,
                                                  end_time=today_unix_timestamp)
    df = pd.DataFrame.from_records(historical)
    df.drop(['time'], axis=1, inplace=True)
    df.drop(['startTime'], axis=1, inplace=True)
    return df
