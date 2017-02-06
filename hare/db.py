# -*- coding: utf-8 -*-
from threading import local
from functools import wraps

import pymysql

from .table import Model, Table
from .transaction import Transaction
from .column import Column
from .connection import Connection
from .exception import HareException


class Hare(object):
    """DataSource, just a database
    """

    def __init__(self, host=None, user=None,
                 password=None, db=None,
                 charset='utf8'):
        self._tables = {}
        self.db_conf = {
            'host': host,
            'user': user,
            'password': password,
            'db': db,
            'charset': charset,
            'cursorclass': pymysql.cursors.DictCursor
        }
        # transaction manger
        self.tx_manager = local()
        self._conn = Connection(**self.db_conf)
        self.name = db
        self._conn.ping()

    def table(self, table_name=None):
        def decorator(cls):
            self._add_table(table_name, cls)
            return cls
        return decorator

    def _add_table(self, table_name, cls):
        if not issubclass(cls, Model):
            raise HareException(
                u"Class: %s should derive from 'Model'" % cls.__name__)
        table = self._get_table(table_name)
        cls.table = table
        self._tables[table_name] = cls

    def _get_table(self, table_name):
        if table_name not in self._tables:
            table = self._build_table(table_name)
            self._tables[table_name] = table
        return self._tables[table_name]

    def _build_table(self, table_name):
        rows = self._get_table_metadata(table_name)
        return Table(self, table_name, rows)

    def _get_table_metadata(self, table_name):
        sql = u"""SELECT COLUMN_NAME AS column_name,
                     ORDINAL_POSITION As ordinal_position,
                     COLUMN_DEFAULT AS column_default,
                     IS_NULLABLE AS is_nullable,
                     DATA_TYPE AS data_type,
                     CHARACTER_MAXIMUM_LENGTH AS character_maximum_length,
                     CHARACTER_OCTET_LENGTH AS character_octet_length,
                     COLUMN_KEY AS column_key,
                     EXTRA AS extra
                 FROM INFORMATION_SCHEMA.COLUMNS
                 WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s"""
        rows = self._conn.select_many(sql, (table_name, self.name))
        if not rows:
            raise HareException(
                (u"Table: '%s' not exists, please "
                 u"check the table name" % table_name))
        columns = [Column(**row) for row in rows]
        return columns

    def tables(self):
        """table names in this database
        :return:
        """
        return self._tables.keys()

    def get_tx(self):
        """return a new transaction
        """
        self._check_nested_tx()
        self.tx_manager.tx = Transaction(self)
        return self.tx_manager.tx

    def _check_nested_tx(self):
        if hasattr(self.tx_manager, 'tx') and self.tx_manager.tx:
            raise HareException(
                ("Nested transaction is not allowed: "
                 "you shouldn't call @tx within the scope "
                 "of a transaction already existing"))

    def clear_tx(self):
        self.tx_manager.tx = None

    def tx(self, func):
        """a transaction decorator, usage like:

            @haredb.tx
            def func(...):
                ...
        :param func: decorated function
        :return:
        """
        self._check_nested_tx()

        @wraps(func)
        def wrapper(*args, **kwds):
            with self.get_tx() as tx:
                try:
                    ret = func(*args, **kwds)
                except:
                    tx.rollback()
                    raise
                else:
                    tx.commit()
                    return ret
        return wrapper

    @property
    def dbi(self):
        """get a connection(from existing transaction or new one)
        :return: Connection
        """
        try:
            tx = self.tx_manager.tx
        except AttributeError:
            return Connection(**self.db_conf)
        else:
            return tx.get_connection() if tx else Connection(**self.db_conf)

    @dbi.setter
    def dbi(self, val):
        raise HareException('Not allowed')

    @dbi.deleter
    def dbi(self, val):
        raise HareException('Not allowed')
