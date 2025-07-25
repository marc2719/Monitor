from lib import RestMarket, RestPublic
from collections import deque
from db import Table
from db import get_tickers

"""
    Ticker类，负责操作list_tickers列表
"""
class Ticker(Table):
    # _instance = None
    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, controller):
        self.controller = controller
        super().__init__(table_name=self.instId.replace('-', '_'), primary_key={'ts'}, record_cls=None)
        self.market = RestMarket()
        self.instrument = RestPublic().get_public_instruments(instType='SPOT', instId=self.instId)[0]
        # self._mate_datas = get_tickers(table_name=self._table_name, limit=1000)
        # for mate_data in self._mate_datas:
        #    mate_data['last'] = float(mate_data['last'])

    def update_ticker(self):
        try:
            tickers = self.market.get_market_ticker(instId=self.instId)
            for ticker in tickers:
                self._insert(**ticker)
                self._mate_datas.append(ticker)
        except Exception as e:
            print(e)

    @property
    def instId(self):
        return self.controller.instId

    @property
    def ccy(self):
        return str(self.instrument.get('baseCcy'))

    @property
    def last(self):
        return float(self._mate_datas[-1].get('last'))

    @property
    def max(self):
        return max([ float(data.get('last')) for data in self._mate_datas ])

