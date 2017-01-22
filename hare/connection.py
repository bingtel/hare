# -*- coding: utf-8 -*-

import logging

import pymysql


class Connection(object):
    """DB Connection
    """
    def __init__(self, autocommit=True, **db_conf):
        self._conn = pymysql.connect(**db_conf)
        self._conn.autocommit(autocommit)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def autocommit(self, autocommit):
        self._conn.autocommit(autocommit)

    @staticmethod
    def _do_execute(sql, args, func, log_level=logging.INFO):
        logging.log(log_level, sql, args)
        affected = func(sql, args)
        return affected

    def select(self, sql, args=None, result_type=dict):
        """
        :param sql: sql to be executed
        :param args: sql args
        :type args: dict, tupe, list
        :param result_type: object type of the reselt
        :type result_type: dict, subclass of `Model`
        :return: None or a data object
        """
        self._do_execute(sql, args, self._cursor.execute)
        if result_type == dict:
            return self._cursor.fetchone()
        return result_type(**self._cursor.fetchone())

    def select_many(self, sql, args=None):
        """
        :param sql: sql to be executed
        :param args: sql args
        :type args: dict, tupe, list
        :return: rows, a tuple
        """
        self._do_execute(sql, args, self._cursor.execute)
        rows = self._cursor.fetchall()
        return rows

    def modify(self, sql, args=None):
        return self._do_execute(sql, args, self._cursor.execute)

    def modify_many(self, sql, args):
        return self._do_execute(sql, args, self._cursor.executemany)

    def commit(self):
        self._conn.commit()
        self._conn.autocommit(True)

    def rollback(self):
        self._conn.rollback()
        self._conn.autocommit(True)

    def ping(self):
        """test whether this connection is valid
        """
        self._conn.ping()

    def get_insert_id(self):
        return self._conn.insert_id()

    def close(self):
        if self._conn:
            self._conn.close()
        self._conn, self._cursor = None, None
