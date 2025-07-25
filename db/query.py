from .connection import Connection

mysql = Connection()

def get_rest_mode():
    return mysql.query(table_name='request_mode')

def get_one_day_orders():
    return mysql.select(sql_name= 'get_one_day_orders')

def get_money_balances():
    return mysql.select(sql_name='get_money_balances')

def get_increment():
    return mysql.select(sql_name='get_increment')

def create_ticker_table(inst_id):
    mysql.write(sql_name='create_ticker_table', sql_param=inst_id.replace('-', '_'))

def get_tickers(table_name, limit):
    return mysql.select(sql_name='get_tickers', sql_param=table_name, sql_arg=limit)

def insert_order_data(order):
    mysql.write(
        sql_name='insert_order_data',
        command='INSERT',
        sql_arg=(
            0 if order.get('ordId') == '' else int(order.get('ordId')),
            str(order.get('clOrdId')),
            str(order.get('ordType')),
            str(order.get('instType')),
            str(order.get('instId')),
            str(order.get('tag')),
            str(order.get('ccy')),
            0 if order.get('px') == '' else float(order.get('px')),
            0 if order.get('sz') == '' else float(order.get('sz')),
            0 if order.get('pnl') == '' else float(order.get('pnl')),
            str(order.get('side')),
            str(order.get('tdMode')),
            0 if order.get('accFillSz') == '' else float(order.get('accFillSz')),
            0 if order.get('fillPx') == '' else float(order.get('fillPx')),
            0 if order.get('tradeId') == '' else int(order.get('tradeId')),
            0 if order.get('fillSz') == '' else float(order.get('fillSz')),
            0 if order.get('fillTime') == '' else int(order.get('fillTime')),
            order.get('fill_datetime'),
            0 if order.get('avgPx') == '' else float(order.get('avgPx')),
            str(order.get('state')),
            0 if order.get('lever') == '' else float(order.get('lever')),
            0 if order.get('tpTriggerPx') == '' else float(order.get('tpTriggerPx')),
            0 if order.get('tpOrdPx') == '' else float(order.get('tpOrdPx')),
            str(order.get('tpTriggerPxType')),
            0 if order.get('slOrdPx') == '' else float(order.get('slOrdPx')),
            0 if order.get('slTriggerPx') == '' else float(order.get('slTriggerPx')),
            str(order.get('slTriggerPxType')),
            str(order.get('feeCcy')),
            0 if order.get('fee') == '' else float(order.get('fee')),
            str(order.get('rebateCcy')),
            0 if order.get('rebate') == '' else float(order.get('rebate')),
            str(order.get('category')),
            0 if order.get('uTime') == '' else int(order.get('uTime')),
            order.get('u_datetime'),
            0 if order.get('cTime') == '' else int(order.get('cTime')),
            order.get('c_datetime'),
            str(order.get('posSide'))
        )
    )

