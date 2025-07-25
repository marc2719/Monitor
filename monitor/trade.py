from lib import RestOrder
from .money import MoneyManagement
from db import Record, Table, insert_order_data
from time import sleep

class Order(Record):
    def __init__(self, table, mate_data):
        super().__init__(table=table, mate_data=mate_data)
        self.controller = table.controller
        self.restorder = RestOrder()
    
    @property
    def id(self):
        return self._mate_data.get('id')

    @property
    def order_id(self):
        return '{0}{1:0>11}'.format(self.controller.ccy, self.id)

class Trade(Table):
    def __init__(self, controller):
        super().__init__(table_name='porders', primary_key={'id'}, record_cls=Order)
        self.controller = controller
        self.restorder = RestOrder()

    @property
    def moneys(self):
        return self.controller.moneys

    @property
    def instId(self):
        return self.controller.instId

    @property
    def logger(self):
        return self.controller.logger

    def sync_order_px(self, ordId):
        print(ordId)
        order_datas = list()
        while len(order_datas) == 0:
            orders = self.restorder.get_orders_history(instType='SPOT', instId=self.instId)
            order_datas = [ data for data in orders if int(data.get('ordId')) == int(ordId) ]
            sleep(1)
        px = 0
        order_data = order_datas[0]
        print(order_data)
        if order_data.get('side') == 'sell' and order_data.get('ordId') == ordId:
            px = float(order_data.get('accFillSz')) * float(order_data.get('avgPx')) + float(order_data.get('fee'))
        if order_data.get('side') == 'buy' and order_data.get('ordId') == ordId:
            px = float(order_data.get('accFillSz')) + float(order_data.get('fee'))
        insert_order_data(order=order_data)
        return px

    def start_order(self,**kwargs):
        order_result = self.restorder.order(**kwargs)
        print(order_result)
        result = dict()
        if isinstance(order_result, list):
            result = order_result[0]
            result['px'] = self.sync_order_px(ordId = result.get('ordId'))
        if isinstance(order_result, dict) and ('data' in order_result):
            result = order_result.get('data')[0]
            result['px'] = 0
            del result['ordId']
        print(result)
        self._records[0]._update(**result)
        self.logger.info(f'Order Result: {order_result}')
        return result.get('px', 0)

    def sell_market(self):
        """
        功能：按市场价卖出
        """
        if self.moneys.balance <= 0:
            return False

        moneys = self.controller.moneys
        money = self.moneys.avail_balance_money()
        order_data = {
            'controller_id': self.controller.id,
            'instId': self.instId,
            'tdMode': 'cash',
            'side': 'sell',
            'ordType': 'market',
            'sz': str(money.balance)
        }
        self.logger.info(f'Order Data: {order_data}')
        order_id = self._insert(**order_data)
        self._get_records(id=order_id)
        del order_data['controller_id']
        order_data['clOrdId'] = self._records[0].order_id
        px = self.start_order(**order_data)
        money.update(usdt=px, side='sell', clOrdId=self._records[0].order_id, balance=0)

    def buy_market(self, sz):
        """
        功能：按市场价买入
        """
        if self.moneys.usdt <= 0:
            return False

        moneys = self.controller.moneys
        money = self.moneys.avail_usdt_money()
        order_data = {
            'controller_id': self.controller.id,
            'instId': self.instId,
            'tdMode': 'cash',
            'side': 'buy',
            'ordType': 'market',
            'sz': str(money.usdt)
        }
        self.logger.info(f'Order Data: {order_data}')
        order_id = self._insert(**order_data)
        self._get_records(id=order_id)
        del order_data['controller_id']
        order_data['clOrdId'] = self._records[0].order_id
        px = self.start_order(**order_data)
        money.update(balance=px, side='buy', clOrdId=self._records[0].order_id)
