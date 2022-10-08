import logging
from typing import List

from ftx.indicators import *
from ftx.tradingfunctions import *

live_sma = liveSMA()

class Bot1():
    
    def __init__(self, api_key, api_secret):

        self.botInfo = [input("Bot 1 asks, what is the most recent type of confirmation signal? UT for buy or DT for sell?"),
                        input("Bot 1 asks, what is the current trend catcher state? CD for red or CU for green.")]
        self.tradingViewInfo = None
        self.accRisk = 0.02
        self.name = 'bot1'
        self.port = 0
        self.live_trades_info = {}
        self.client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name='bot1')
        self.SR_levels = {'AVG': None, 'R1': None, 'R2': None, 'S1': None, '21': None}
        
        for i in self.client.get_balances():
            self.port += i['total']

    def update(self, data: List[str]):
        logging.info('bot1 received info from T V alert')
        self.tradingViewInfo = data
        pos = 0

        for i in self.client.get_positions():
            if i['future'] == f'{self.tradingViewInfo[0]}-PERP':
                pos = i['size']

        "MARKET SIGNAL CLOSE"
        if self.tradingViewInfo[1][0] == "C":
            self.botInfo[1] = self.tradingViewInfo[1]
        elif self.tradingViewInfo[1][1] == "T":
            self.botInfo[0] = self.tradingViewInfo[1]

        if (self.tradingViewInfo[1] == "UT" or self.tradingViewInfo[1] == "ES") and\
                pos < 0:
            exit_trade(self.tradingViewInfo[0], 'sell', self.client)
            logging.info(f'bot1 exit sell at: {self.tradingViewInfo[2]}')
            
        elif (self.tradingViewInfo[1] == "DT" or self.tradingViewInfo[1] == "EB") and\
                pos > 0:
            exit_trade(self.tradingViewInfo[0], 'buy', self.client)
            logging.info(f'bot1 exit buy at: {self.tradingViewInfo[2]}')

        if self.tradingViewInfo[1] == "OU":
            self.check_trade()
        elif self.tradingViewInfo[1] == "OD":
            self.check_trade()

    def check_trade(self):

        self.port = 0
        
        for i in self.client.get_balances():
            self.port += i['total']

        if self.botInfo[0] == "UT" and self.botInfo[1] == "CU" and self.tradingViewInfo[1] == "OU" and\
                self.client.get_positions()[0]['size'] == 0:
            sl = calc_sl(self.tradingViewInfo[2], 'buy', 1)
            tp = calc_tp(self.tradingViewInfo[2], 'buy', 1)
            pos_size = calc_pos_size(port=self.port, entry_price=self.tradingViewInfo[2], side='buy',
                                     acc_risk=self.accRisk, sl=sl)
            enter_buy(market=self.tradingViewInfo[0], price=self.tradingViewInfo[2], size=pos_size,
                      sl=sl, tp=tp, client=self.client)
            self.live_trades_info[self.tradingViewInfo[0]] = []
            self.live_trades_info[self.tradingViewInfo[0]].append(self.tradingViewInfo[2])
            self.live_trades_info[self.tradingViewInfo[0]].append(None)
            self.live_trades_info[self.tradingViewInfo[0]].append('buy')
            logging.info(f'bot1 entered buy at: {self.tradingViewInfo[2]}')

        elif self.botInfo[0] == "DT" and self.botInfo[1] == "CD" and self.tradingViewInfo[1] == "OD" and\
                self.client.get_positions()[0]['size'] == 0:
            sl = calc_sl(self.tradingViewInfo[2], 'sell', 1)
            tp = calc_tp(self.tradingViewInfo[2], 'sell', 1)
            pos_size = calc_pos_size(port=self.port, entry_price=self.tradingViewInfo[2], side='sell',
                                     acc_risk=self.accRisk, sl=sl)
            enter_sell(market=self.tradingViewInfo[0], price=self.tradingViewInfo[2], size=pos_size,
                       sl=sl, tp=tp, client=self.client)
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
            if (self.live_trades_info[i][1] - self.live_trades_info[i][0]) * 100 > 0.5:
                update_sl(market=i, new_sl=self.live_trades_info[i][0], client=self.client)
        """for i in self.live_trades_info:
            if self.live_trades_info[i][1] >= self.SR_levels['R1'] and self.live_trades_info[2] == 'buy':
                update_sl(market=i, new_sl=self.live_trades_info[i][0], client=client)
            elif self.live_trades_info[i][1] <= self.SR_levels['S1'] and self.live_trades_info[2] == 'sell':
                update_sl(market=i, new_sl=self.live_trades_info[i][0], client=client)"""

    def start_bot(self):
        pass

    def to_string(self):
        return "bot1"


class Bot2():

    def __init__(self, api_key, api_secret):
        self.client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name='bot2')
        self.port = 0
        self.price_data = None

        for i in self.client.get_balances():
            self.port += i['total']

    def start_bot(self):
        live_sma.attach(self)

    def to_string(self):

        return "bot2"
