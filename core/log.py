# -*- coding:utf-8 -*-

import logging
from setting import log_dir
from datetime import datetime, timedelta
# 设置打印日志的级别，level级别以上的日志会打印出
# level=logging.DEBUG 、INFO 、WARNING、ERROR、CRITICAL

class Logger(object):
    def __init__(self, log_name) -> None:
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        self.file_handle = logging.FileHandler(filename=f'{log_dir}{log_name}.log', mode='a', encoding='utf8')
        self.file_handle.setLevel(level=logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        self.formatter.converter = self.beijing
        self.file_handle.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handle)

    def beijing(sec, day):
        return (datetime.now() + timedelta(hours=8)).timetuple()
