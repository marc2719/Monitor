from monitor.money import MoneyManagement
from db.connection import Connection
from monitor.monitor import Monitor


if __name__ == '__main__':
    app = Monitor()
    app.start()
