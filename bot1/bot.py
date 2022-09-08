from client import FtxClient
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('api_key_bot1')
api_secret = os.getenv('api_secret_bot1')
client = FtxClient(api_key=api_key, api_secret=api_secret)


class Bot():

    def __init__(self, confirmation, trendcatcher):
        self.botInfo = [confirmation, trendcatcher]
        self.tradingViewInfo = None
        self.accRisk = 0.2
        self.port = 0
        for i in client.get_balances():
            self.port += i['total']

    def update(self, data):



        self.tradingViewInfo = data.split()
        self.tradingViewInfo[0] = self.tradingViewInfo[0][:-4]
        self.tradingViewInfo[2] = int(self.tradingViewInfo[2])

        if len(self.tradingViewInfo) == 4:
            if self.tradingViewInfo[1][0] == "C":
                self.botInfo[1] = self.tradingViewInfo[1]
            else:
                self.botInfo[0] = self.tradingViewInfo[1]

        print(self.botInfo)

        if (self.tradingViewInfo[1] == "UT" or self.tradingViewInfo[1] == "EB") and client.get_positions()[0]['size'] < 0:
            self.exitTrade(self.tradingViewInfo[0], 'sell')
        elif (self.tradingViewInfo[1] == "DT" or self.tradingViewInfo[1] == "ES") and client.get_positions()[0]['size'] > 0:
            self.exitTrade(self.tradingViewInfo[0], 'buy')

        if self.tradingViewInfo[1] == "OU":
            self.checkTrade()
        elif self.tradingViewInfo[1] == "OD":
            self.checkTrade()

    def checkTrade(self):
        self.port = 0
        for i in client.get_balances():
            self.port += i['total']
        if self.botInfo[0] == "UT" and self.botInfo[1] == "CU" and self.tradingViewInfo[1] == "OU" and client.get_positions()[0]['size'] == 0:
            self.enterBuy(self.tradingViewInfo[0], self.tradingViewInfo[2], self.calcPosSize(self.tradingViewInfo[2], 'buy'),
                           self.calcSL(self.tradingViewInfo[2], 'buy'), self.calcTP(self.tradingViewInfo[2], 'buy'))

        elif self.botInfo[0] == "DT" and self.botInfo[1] == "CD" and self.tradingViewInfo[1] == "OD" and client.get_positions()[0]['size'] == 0:
            self.enterSell(self.tradingViewInfo[0], self.tradingViewInfo[2], self.calcPosSize(self.tradingViewInfo[2], 'sell'),
                            self.calcSL(self.tradingViewInfo[2], 'sell'), self.calcTP(self.tradingViewInfo[2], 'sell'))

    def handleExitSignal(self, exitType):
        if client.get_positions()[0]['size'] != 0:
            if exitType == "ES":
                self.exitTrade(self.tradingViewInfo[0], 'sell')
            elif exitType == "EB":
                self.exitTrade(self.tradingViewInfo[0], 'buy')

    def calcSL(self, price, type):
        if type == 'sell':
            sl = price + price * 0.01
        elif type == 'buy':
            sl = price - price * 0.01
        return sl

    def calcPosSize(self, entryPrice, type):
        riskAmount = self.port * self.accRisk
        SL = self.calcSL(entryPrice, type)
        if type == 'sell':
            SLDistance = SL - entryPrice
        else:
            SLDistance = entryPrice + SL
        posSize = riskAmount / SLDistance
        return posSize

    def calcTP(self, price, type):
        if type == 'sell':
            tp = price - price * 0.01
        elif type == 'buy':
            tp = price + price * 0.01
        return tp

    def exitTrade(self, market, type):
        if type == 'sell':
            client.place_order(
                market=f'{market}-PERP',
                side="buy",
                price=client.get_trades('BTC-PERP')[0]['price'],
                reduce_only=True,
                size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
            )
        elif type == 'buy':
            client.place_order(
                market=f'{market}-PERP',
                side="sell",
                price=client.get_trades('BTC-PERP')[0]['price'],
                reduce_only=True,
                size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
            )

    def enterBuy(self, market, price, size, sl, tp):
        client.place_order(
            market=f'{market}-PERP',
            side="buy",
            price=price,
            size=size
        )

        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=size + (size * 2),
            type='stop',
            reduce_only=True,
            trigger_price=sl
        )

        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=size + (size * 2),
            type='take_profit',
            reduce_only=True,
            trigger_price=tp
        )

    def enterSell(self, market, price, size, sl, tp):

        client.place_order(
            market=f'{market}-PERP',
            side="sell",
            type='limit',
            price=price,
            size=size
        )

        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=size + (size * 2),
            type='stop',
            reduce_only=True,
            trigger_price=sl
        )

        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=size + (size * 2),
            type='takeProfit',
            reduce_only=True,
            trigger_price=tp
        )

    def setAccRisk(self, accRisk):
        self.accRisk = accRisk

    def setInitialState(self, confirmation, trendcatcher):
        self.botInfo[0] = confirmation
        self.botInfo[1] = trendcatcher


bot = Bot()
bot.enterBuy()