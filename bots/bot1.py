import os
import logging
import sys
import threading
import time

from dotenv import load_dotenv

from ftx.tradingfunctions import *

load_dotenv()

api_key = os.getenv('api_key_main')
api_secret = os.getenv('api_secret_main')

client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name='bot1')

if sys.platform.startswith('win'):
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '\\' + 'bot.log'
else:
    logfile_path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'bot.log'

logging.basicConfig(filename=logfile_path, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s')


class Bot:
    
    def __init__(self):

        self.botInfo = [input("Most recent type of confirmation signal? UT or DT?"),
                        input("Trend catcher state? CD for red or CU for green.")]
        self.tradingViewInfo = None
        self.accRisk = 0.02
        self.port = 0
        self.live_trades_info = {}
        self.SR_levels = {'AVG': None, 'R1': None, 'R2': None, 'S1': None, '21': None}
        
        for i in client.get_balances():
            self.port += i['total']

    def update(self, data: str):
        logging.info('bot1 received info from T V alert')
        self.tradingViewInfo = data.split()
        self.tradingViewInfo[0] = self.tradingViewInfo[0][:-4]
        self.tradingViewInfo[2] = int(self.tradingViewInfo[2])
        pos = 0

        for i in client.get_positions():
            if i['future'] == f'{self.tradingViewInfo[0]}-PERP':
                pos = i['size']

        if len(self.tradingViewInfo) == 4:
            if self.tradingViewInfo[1][0] == "C":
                self.botInfo[1] = self.tradingViewInfo[1]
            else:
                self.botInfo[0] = self.tradingViewInfo[1]

        if (self.tradingViewInfo[1] == "UT" or self.tradingViewInfo[1] == "ES") and\
                pos < 0:
            exit_trade(self.tradingViewInfo[0], 'sell', client)
            logging.info(f'bot1 exit sell at: {self.tradingViewInfo[2]}')
            
        elif (self.tradingViewInfo[1] == "DT" or self.tradingViewInfo[1] == "EB") and\
                pos > 0:
            exit_trade(self.tradingViewInfo[0], 'buy', client)
            logging.info(f'bot1 exit buy at: {self.tradingViewInfo[2]}')

        if self.tradingViewInfo[1] == "OU":
            self.check_trade()
        elif self.tradingViewInfo[1] == "OD":
            self.check_trade()

    def check_trade(self):

        self.port = 0
        
        for i in client.get_balances():
            self.port += i['total']

        if self.botInfo[0] == "UT" and self.botInfo[1] == "CU" and self.tradingViewInfo[1] == "OU" and\
                client.get_positions()[0]['size'] == 0:
            sl = calc_sl(self.tradingViewInfo[2], 'buy', 1)
            tp = calc_tp(self.tradingViewInfo[2], 'buy', 1)
            pos_size = calc_pos_size(port=self.port, entry_price=self.tradingViewInfo[2], side='buy',
                                     acc_risk=self.accRisk, sl=sl)
            enter_buy(market=self.tradingViewInfo[0], price=self.tradingViewInfo[2], size=pos_size,
                      sl=sl, tp=tp, client=client)
            self.live_trades_info[self.tradingViewInfo[0]] = []
            self.live_trades_info[self.tradingViewInfo[0]].append(self.tradingViewInfo[2])
            self.live_trades_info[self.tradingViewInfo[0]].append(None)
            self.live_trades_info[self.tradingViewInfo[0]].append('buy')
            logging.info(f'bot1 entered buy at: {self.tradingViewInfo[2]}')

        elif self.botInfo[0] == "DT" and self.botInfo[1] == "CD" and self.tradingViewInfo[1] == "OD" and\
                client.get_positions()[0]['size'] == 0:
            sl = calc_sl(self.tradingViewInfo[2], 'sell', 1)
            tp = calc_tp(self.tradingViewInfo[2], 'sell', 1)
            pos_size = calc_pos_size(port=self.port, entry_price=self.tradingViewInfo[2], side='sell',
                                     acc_risk=self.accRisk, sl=sl)
            enter_sell(market=self.tradingViewInfo[0], price=self.tradingViewInfo[2], size=pos_size,
                       sl=sl, tp=tp, client=client)
            self.live_trades_info[self.tradingViewInfo[0]] = [None, None, None]
            self.live_trades_info[self.tradingViewInfo[0]][0] = self.tradingViewInfo[2]
            self.live_trades_info[self.tradingViewInfo[0]].append('sell')
            logging.info(f'bot1 entered sell at: {self.tradingViewInfo[2]}')

    def update_trade_info(self, market: str, price: float):
        if market in self.live_trades_info:
            self.live_trades_info[market][1] = price
            self.handle_trade_updates()


    def remove_trade_info(self, market: str):
        self.live_trades_info.pop(market, None)

    def handle_trade_updates(self):

        for i in self.live_trades_info:
            if self.live_trades_info[i][1] >= self.SR_levels['R1'] and self.live_trades_info[2] == 'buy':
                update_sl(market=i, new_sl=self.live_trades_info[i][0], client=client)
            elif self.live_trades_info[i][1] <= self.SR_levels['S1'] and self.live_trades_info[2] == 'sell':
                update_sl(market=i, new_sl=self.live_trades_info[i][0], client=client)


def handle_webhook_data(data: str = None):
    bot.update(data)


def live_trade_price_data(client: FtxClient):
    print('threadstart')
    while True:
        for i in client.get_positions():
            if i['size'] > 0:
                bot.update_trade_info(market=i['future'], price=client.get_single_market(market=i['future'])['last'])
            else:
                bot.remove_trade_info(market=i['future'])
        time.sleep(1)


def start_bot():
    threading.Thread(target=live_trade_price_data(client=client)).start()


bot = Bot()
