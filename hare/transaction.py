# -*- coding: utf-8 -*-

"""Nested transaction is not implemented now.
"""
import logging
from .connection import Connection
from .exception import HareException


class Transaction(object):
    """Transaction for mysql connection
    """
    def __init__(self, hare):
        self.hare = hare
        self._conn = Connection(autocommit=False,
                                **self.hare.db_conf)
        self._dirty = True

    def __enter__(self):
        self._check_status()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(exc_type, exc_val, exc_tb)
        if self._dirty:
            self.rollback()
            raise HareException(
                'Transaction exited without rollback()/commit()')
        self._conn.autocommit(True)
        self.hare.clear_tx()

    def get_connection(self):
        self._check_status()
        return self._conn

    def rollback(self):
        self._check_status()
        self._conn.rollback()
        self._dirty = False

    def commit(self):
        self._check_status()
        self._conn.commit()
        self._dirty = False

    def is_finished(self):
        """whether transaction is commit() or rollback() already
        :return: True, transaction is finished
                 False, transaction is not finished
        """
        return self._dirty is False

    def _check_status(self):
        if self.is_finished():
            raise HareException(
                'Transaction is already finished with rollback()/commit()')
