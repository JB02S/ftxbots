import datetime
import time

import pandas as pd

from ftx.rest.client import FtxClient


def get_past_hour_historical_info(client: FtxClient, market: str, seconds_ago, timeframe):

    today_unix_timestamp = time.mktime(datetime.datetime.now().timetuple())
    hour_ago = datetime.datetime.now() - datetime.timedelta(seconds=seconds_ago)
    hour_ago_unix_timestamp = time.mktime(hour_ago.timetuple())

    historical = client.get_historical_prices(market=market, resolution=timeframe, start_time=hour_ago_unix_timestamp,
                                                  end_time=today_unix_timestamp)
    df = pd.DataFrame.from_records(historical)
    df.drop(['time'], axis=1, inplace=True)
    df.drop(['startTime'], axis=1, inplace=True)
    return df


class Subject:
    """Represents what is being observed"""

    def __init__(self):

        """create an empty observer list"""

        self._observers = []

    def notify(self, modifier=None):

        """Alert the observers"""

        for observer in self._observers:
            if modifier != observer:
                observer.update(self)

    def attach(self, observer):

        """If the observer is not in the list,
        append it into the list"""

        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):

        """Remove the observer from the observer list"""

        try:
            self._observers.remove(observer)
        except ValueError:
            pass


class liveSMA(Subject):

    def indicator(self, length, client, timeframe):

        df = get_past_hour_historical_info(client, 'BTC-PERP', length, timeframe)['close']
        df = df.rolling(length // timeframe).sum()
        df.dropna(inplace=True)
        SMA = df.values / (length // timeframe)
        self.notify(modifier=SMA)
