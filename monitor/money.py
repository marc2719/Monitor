from db import Table, Record
from lib import RestAccount

class Money(Record):
    def __init__(self, mate_data, table):
        super().__init__(table=table, mate_data=mate_data)

    def __eq__(self, other):
        if isinstance(other, Money):
            return self.instId == other.instId and self.no == self.no
        return False

    @property
    def instId(self):
        return self._mate_data.get('instId', None)

    @property
    def no(self):
        return self._mate_data.get('no', None)

    @property
    def balance(self):
        return self._mate_data.get('balance', None)

    @balance.setter
    def balance(self, value):
        self._mate_data['balance'] = value
        super()._update(balance=value)

    @property
    def usdt(self):
        return self._mate_data.get('usdt', None)

    @usdt.setter
    def usdt(self, value):
        self._mate_data['usdt'] = value
        super()._update(usdt=value)

    @property
    def clOrdId(self):
        return self._mate_data.get('clOrdId', None)

    @clOrdId.setter
    def clOrdId(self, value):
        self._mate_data['clOrdId'] = value
        super()._update(clOrdId=value)

    @property
    def side(self):
        return self._mate_data.get('side', None)

    @side.setter
    def side(self, value):
        self._mate_data['side'] = value
        super()._update(side=value)

    def update(self, **kwargs):
        self._mate_data.update(kwargs)
        super()._update(**kwargs)

class MoneyManagement(Table):
    def __init__(self, controller):
        super().__init__(table_name='money', primary_key={'instId', 'no'}, record_cls=Money)
        self.controller = controller

    def gen_moneys(self, count):
        if self.check_records(instId=self.instId) is True:
            self.gen_money_objects()
            return
        record_balance = self.balance_ccy / count
        datas = [{'instId': self.instId, 'controller_id': self.controller.id, 'balance': record_balance, 'init_balance': record_balance, 'no': i} for i in range(count)]
        for data in datas:
            self._insert(**data)
        self.gen_money_objects()

    def gen_money_objects(self):
        self._get_records(instId=self.instId)

    @property
    def instId(self):
        return self.controller.instId

    @property
    def usdt(self):
        return sum([float(money.usdt) for money in self._records])

    def avail_usdt_money(self):
        usdt = [money for money in self._records if money.usdt > 0 and money.balance == 0]
        return None if len(usdt) <= 0 else usdt[0]

    @property
    def balance(self):
        return sum([float(money.balance) for money in self._records])

    @property
    def balance_ccy(self):
        """
        获取货币余额
        """
        account = RestAccount()
        balances = account.get_account_balance(ccy=self.controller.ccy)
        self.controller.logger.info(f'balances: {balances}')
        if len(balances) == 0:
            return 0
        else:
            return float(balances[0].get('availEq'))

    def avail_balance_money(self):
        balances = [money for money in self._records if money.balance > 0 and money.usdt == 0]
        return None if len(balances) <= 0 else balances[0]

    def get_money(self, no):
        return [money for money in self._records if money.no == no][0]

