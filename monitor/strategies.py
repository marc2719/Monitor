from abc import ABCMeta, abstractmethod

from json import loads


class Strategy(object, metaclass=ABCMeta):
    """
    类名:Strategy
    功能:策略类，负责对获取到的数据，按策略的条件判断，是否触发买入或卖出操作
    """
    def __init__(self, controller):
        self.controller = controller
        self.strategy_data = loads(controller._mate_data.get('strategy_info'))

    @property
    def ticker(self):
        return self.controller.ticker

    # 是否符合买入条件
    @abstractmethod
    def buy_check(self):
        pass

    # 是否符合卖出条件
    @abstractmethod
    def sell_check(self):
        pass


class MiniIncreaseStrategy(Strategy):
    def __init__(self, controller):
        super().__init__(controller=controller)
        self.trigger = float(self.strategy_data.get("trigger"))
        self.pre_times = int(self.strategy_data.get("pre_times"))
        self.avg_times = int(self.strategy_data.get("avg_times"))
        self.buy_trigger = None
        self.sell_max = None

    @property
    def mini_increment(self):
        return self.ticker.mini_increment(
            pre_times=self.pre_times,
            avg_times=self.avg_times
        )

    def sell_check(self):
        self.controller.logger.info(msg=f'Sell Check: {self.ticker.last} / {self.ticker.increment_base} | Mini Increment: {self.mini_increment} | Trigger: {self.trigger} | Mini_Avg: {self.ticker.mini_increment_avg}')
        if not self.mini_increment:
            return False
        if self.mini_increment > self.ticker.mini_increment_avg:
            return False
        if self.mini_increment >= self.trigger:
            return True
        return False

    def buy_check(self):
        if self.controller.buy_money.buy_base_check(last=self.controller.ticker.last):
            self.controller.logger.info(msg=str(self.strategy.mini_increment))
            if self.mini_increment >= -0.01:
                return True

        return False

    @staticmethod
    def validate(StrategyName):
        return True if StrategyName == 'MiniIncreaseStrategy' else False


class MaximumDrawdown(Strategy):
    
    def __init__(self, controller):
        super().__init__(controller=controller)
        self.mdd = float(self.strategy_data.get("mdd"))

    def sell_check(self):
        self.controller.logger.info(msg=f'Sell Check: {self.ticker.last} | MaximumDrawdown: {self.mdd} | max:{self.ticker.max} | Trigger: {self.ticker.max * (1-self.mdd)}')
        if self.ticker.last < self.ticker.max * (1-self.mdd) and self.ticker.last > 0.03:
            return True
        return False

    def buy_check(self):
        return False

    @staticmethod
    def validate(StrategyName):
        return True if StrategyName == 'MaximumDrawdown' else False


def strategy_maker(strategy_name, controller):
    for strategy_cls in Strategy.__subclasses__():
        if strategy_cls.validate(strategy_name):
            return strategy_cls(controller)
