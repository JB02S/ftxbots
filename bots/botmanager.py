import logging
import os
import sys
import threading

from bots.bot1 import Bot1
from ftx.rest.client import FtxClient

api_key = os.getenv('api_key_main')
api_secret = os.getenv('api_secret_main')

client = FtxClient(api_key=api_key, api_secret=api_secret)

if sys.platform.startswith('win'):
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '\\' + 'bot.log'
else:
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'bot.log'

logging.basicConfig(filename=logfile_path, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')

bot1 = Bot1(client_reference=client)

bot_arr = [bot1]


def live_trade_price_data(client: FtxClient):
    logging.info('bot starting live price data thread')

    while True:
        pass
        """for i in client.get_positions():
            if i['size'] > 0:
                Bot1.update_trade_info(market=i['future'], price=client.get_single_market(market=i['future'])['last'])
            else:
                Bot1.remove_trade_info(market=i['future'])
"""

def start_price_data_thread():
    threading.Thread(target=live_trade_price_data(client=client)).start()


def handle_webhook_data(data: str):
    data_arr = data.split()
    data_arr[1] = data_arr[1][:-4]
    data_arr[3] = int(data_arr[3])
    for bots in bot_arr:
        if bots.toString == data[0]:
            data_arr.pop(0)
            bots.update(data_arr)
