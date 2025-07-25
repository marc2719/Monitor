from .strategies import strategy_maker
from core import Logger, Ticker
from lib import RestOrder
from threading import Thread

from time import sleep
from db import Record, create_ticker_table
from .money import MoneyManagement
from .trade import Trade

class Controller(Record):
    '''
    类名:Controller
    功能：控制类，开始监控的入口，负责创建并初始化所有对象，并进入主循环。
    '''
    def __init__(self, mate_data, table):
        super().__init__(table=table, mate_data=mate_data)
        self.ticker = Ticker(controller=self)
        self.strategy = strategy_maker(strategy_name=self._mate_data.get('strategy_name'), controller=self)
        self.logger = Logger(log_name=self.instId).logger
        self.moneys = MoneyManagement(controller=self)

    def __eq__(self, other):
        if isinstance(other, Controller):
            return self.id == other.id
        return False

    @property
    def instId(self):
        return self._mate_data.get('instId', None)

    @property
    def id(self):
        return self._mate_data.get('id', None)

    @property
    def interval_time(self):
        return self._mate_data.get('interval_time', 30)

    def init_controller(self):
        self.logger.info(msg=f'{self._mate_data}')
        self.logger.info(msg='Controller ID: {self.id}开始初始化Controller......')
        self.logger.info('策略创建成功！')
        create_ticker_table(inst_id=self.instId)
        self.moneys.gen_moneys(count=int(self._mate_data.get('money_split')))

    @property
    def ccy(self):
        return self.ticker.ccy
        
    def sell_check(self):
        try:
            if self.moneys.balance > 0 and self.strategy.sell_check():
                trader = Trade(controller=self)
                trader.sell_market()
        except Exception as e:
            self.logger.error(msg=e)

    def buy_check(self):
        try:
            if self.moneys.usdt > 0 and self.strategy.buy_check():
                trader = Trade(controller=self)
                Thread(target=trader.buy_market).start()
        except Exception as e:
            self.logger.error(msg=e)

    def check(self):
        self.ticker.update_ticker()
        self.sell_check()
        self.buy_check()

