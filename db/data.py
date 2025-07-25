from abc import ABCMeta, abstractmethod

# connection 不存在于模块里，只提供模块内的调用。
from .connection import Connection


class Table(object, metaclass=ABCMeta):
    def __init__(self, table_name:str, primary_key:set, record_cls):
        self._table_name = table_name
        self._primary_key = primary_key
        self._mate_datas = list()
        self._records = list()
        self._mysql_conn = Connection()
        self._record_cls = record_cls

    def __getitem__(self, index):
        return self._records[index]

    def _query(self, **kwargs):
        return self._mysql_conn.query(table_name=self._table_name, cond_items=kwargs)

    def _insert(self, **kwargs):
        return self._mysql_conn.insert(table_name=self._table_name, sql_items=kwargs, get_id=True)

    def _get_records(self, **kwargs):
        self._mate_datas = self._query(**kwargs)
        self._records.clear()
        self._records = [ self._record_cls(table=self, mate_data=mate_data) for mate_data in self._mate_datas ]

    def check_records(self, **kwargs):
        datas = self._query(**kwargs)
        return False if len(datas) == 0 else True


class Record(object, metaclass=ABCMeta):
    def __init__(self, table:Table, mate_data:dict):
        self._table = table
        self._mate_data = mate_data

    @property
    def _primary_key(self):
        return self._table._primary_key

    @property
    def _table_name(self):
        return self._table._table_name

    @property
    def _mysql_conn(self):
        return self._table._mysql_conn

    def _update(self, **kwargs):
        if not self._primary_key.issubset(set(self._mate_data.keys())):
            return False
        conditions = {k: v for k, v in self._mate_data.items() if k in self._primary_key}
        return self._mysql_conn.update(table_name=self._table_name, sql_items=kwargs, cond_items=conditions)

