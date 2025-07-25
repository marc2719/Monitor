from pymysql import connect, cursors

from setting import mysql_host, mysql_port, database, mysql_user, mysql_password, mysql_charset


class Connection(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):

        self.sql_json = None
        self.sql = None
        self.conn = connect(
            host=mysql_host,
            port=mysql_port,
            database=database,
            user=mysql_user,
            password=mysql_password,
            charset=mysql_charset,
            cursorclass=cursors.DictCursor
        )
        self.get_scripts()

    def __del__(self):
        self.conn.close()

    def get_scripts(self):
        sql = """select name, script from monitor.sql_mode"""
        with self.conn.cursor() as cursor:
            cursor.execute(query=sql)
            result = cursor.fetchall()
            self.sql_json = {item.get('name'): item.get('script') for item in result}

    def get_sql(self, sql_name, sql_param: any=None):
        sql = self.sql_json.get(sql_name)
        self.sql = sql if sql_param is None else sql.format(sql_param)

    # SQL读操作
    # noinspection PyBroadException
    def select(self, sql_name: str, rows: int = None, sql_arg: str=None, sql_param: any=None):
        self.get_sql(sql_name=sql_name, sql_param=sql_param)
        if not self.conn.open:
            self.conn.ping(reconnect=True)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query=self.sql, args=sql_arg)
                if rows is None or rows <= 0:
                    result = cursor.fetchall()
                elif rows == 1:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchmany(size=rows)
        except Exception as e:
            return None
        return result

    # SQL写操作
    # noinspection PyBroadException
    def write(self, sql_name: str, command: any='INSERT', sql_arg: any=None, sql_param: any=None):
        self.get_sql(sql_name=sql_name, sql_param=sql_param)
        if not self.conn.open:
            self.conn.ping(reconnect=True)
        try:
            self.conn.begin()
            with self.conn.cursor() as cursor:
                result = cursor.execute(query=self.sql, args=sql_arg)
                if command == 'INSERT':
                    result = self.conn.insert_id()
            self.conn.commit()
        except Exception as e:
            return None
        return result

    def insert(self, table_name: str, sql_items: dict, get_id: bool=False):
        sql = 'REPLACE INTO {0}({1}) VALUES({2});'
        columns = ', '.join([col for col in sql_items.keys()])
        placeholders = ', '.join(['%s'] * len(sql_items))
        sql_arg = tuple(sql_items.values())
        if not self.conn.open:
            self.conn.ping(reconnect=True)
        try:
            self.conn.begin()
            with self.conn.cursor() as cursor:
                result = cursor.execute(query=sql.format(table_name, columns, placeholders), args=sql_arg)
                result = self.conn.insert_id() if get_id else result
            self.conn.commit()
        except Exception as e:
            return None
        return result

    def update(self, table_name: str, sql_items: dict, cond_items: dict):
        sql = 'UPDATE {0} SET {1} WHERE {2};'
        allcolumns = ', '.join([f'{item} = %s' for item in sql_items.keys()])
        conditions = ' AND '.join([f'{item} = %s' for item in cond_items.keys()])
        sql_arg = tuple(sql_items.values()) + tuple(cond_items.values())
        if not self.conn.open:
            self.conn.ping(reconnect=True)
        try:
            self.conn.begin()
            with self.conn.cursor() as cursor:
                cursor.execute(query=sql.format(table_name, allcolumns, conditions), args=sql_arg)
            self.conn.commit()
        except Exception as e:
            return False
        return True

    def query(self, table_name:str, columns:tuple=(), cond_items:dict={}):
        sql1 = 'SELECT {0} FROM {1} WHERE {2};'
        sql2 = 'SELECT {0} FROM {1}'
        allcolumns = ', '.join(columns) if len(columns) > 0 else '*'
        conditions = ' AND '.join([f'{item} = %s' for item in cond_items.keys()])
        sql = sql1.format(allcolumns, table_name, conditions) if len(cond_items) > 0 else sql2.format(allcolumns, table_name)
        sql_arg = tuple(cond_items.values())
        if not self.conn.open:
            self.conn.ping(reconnect=True)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query=sql, args=sql_arg)
                result = cursor.fetchall()
        except Exception as e:
            return None
        return result

    # 只获取一条数据
    def get_one_row(self, sql_name: str, sql_arg: any, default: any=None, field: str=None, sql_param: any=None):
        result = self.select(sql_name=sql_name, rows=1, sql_arg=sql_arg, sql_param=sql_param)
        if result is None:
            return default
        if isinstance(result, dict) and field is not None:
            return result.get(field)
        else:
            return result
