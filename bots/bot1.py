import os

from dotenv import load_dotenv

from ftx.tradingfunctions import *

load_dotenv()

api_key = os.getenv('api_key_main')
api_secret = os.getenv('api_secret_main')

client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name='bot1')


class Bot:
    
    def __init__(self):
        
        self.botInfo = [input("Most recent type of confirmation signal? UT or DT?"),
                        input("Trend catcher state? CD for red or CU for green.")]
        self.tradingViewInfo = None
        self.accRisk = 0.02
        self.port = 0
        
        for i in client.get_balances():
            self.port += i['total']

    def update(self, data: str):

        self.tradingViewInfo = data.split()
        self.tradingViewInfo[0] = self.tradingViewInfo[0][:-4]
        self.tradingViewInfo[2] = int(self.tradingViewInfo[2])

        if len(self.tradingViewInfo) == 4:
            if self.tradingViewInfo[1][0] == "C":
                self.botInfo[1] = self.tradingViewInfo[1]
            else:
                self.botInfo[0] = self.tradingViewInfo[1]

        if (self.tradingViewInfo[1] == "UT" or self.tradingViewInfo[1] == "ES") and\
                client.get_positions()[0]['size'] < 0:
            exit_trade(self.tradingViewInfo[0], 'sell', client)
            
        elif (self.tradingViewInfo[1] == "DT" or self.tradingViewInfo[1] == "EB") and\
                client.get_positions()[0]['size'] > 0:
            exit_trade(self.tradingViewInfo[0], 'buy', client)

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

        elif self.botInfo[0] == "DT" and self.botInfo[1] == "CD" and self.tradingViewInfo[1] == "OD" and\
                client.get_positions()[0]['size'] == 0:
            sl = calc_sl(self.tradingViewInfo[2], 'sell', 1)
            tp = calc_tp(self.tradingViewInfo[2], 'sell', 1)
            pos_size = calc_pos_size(port=self.port, entry_price=self.tradingViewInfo[2], side='sell',
                                     acc_risk=self.accRisk, sl=sl)
            enter_sell(market=self.tradingViewInfo[0], price=self.tradingViewInfo[2], size=pos_size,
                       sl=sl, tp=tp, client=client)
