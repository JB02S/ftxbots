from ftx.tradingfunctions import *


class Bot2:

    def __init__(self, api_key, api_secret):
        self.client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name='bot2')
        self.port = 0

        for i in self.client.get_balances():
            self.port += i['total']

    def start_bot(self):
        pass

    def toString(self):
        return "bot2"
