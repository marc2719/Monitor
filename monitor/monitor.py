from multiprocessing import Process
from time import sleep

from .controller import Controller
from core import mail
from db import Table, Table

class Monitor(Table):
    """
        类名：Monitor
        功能：监控类，负责数据的监控，时时从官方获取数据，并存储到数据库和内存里，是程序的入口
            如果有多个策略，可以开启多进程。
    """
    def __init__(self):
        super().__init__(table_name='controller', primary_key={'id'}, record_cls=Controller)

    def gen_controllers(self):
        self._get_records(disable=0)

    def start_monitor(self):
        for controller in self._records:
            process = Process(
                target=self.ticker_loop,
                name=controller.instId,
                args=(controller, int(controller.interval_time))
            )
            process.start()

    def init_controllers(self):
        for controller in self._records:
            controller.init_controller()

    def start(self):
        self.gen_controllers()
        self.init_controllers()
        mail.start()
        self.start_monitor()

    @staticmethod
    def ticker_loop(controller, interval_time):
        while True:
            controller.check()
            sleep(interval_time)
