# -*- coding: utf-8 -*-

from collections import OrderedDict

from .exception import HareException
from .util import paginate

_COLUMN_KEY_PRI = 'PRI'
_COLUMN_AUTOINCREMENT = 'auto_increment'


class Table(object):

    def __init__(self, hare, table_name, columns):
        """
        :param hare: hare object
        :param table_name:
        :param columns: a list of Column objects
        """
        self.name = table_name
        self.primary_keys = set()
        self.auto_incr_key = None
        self.columns = OrderedDict()
        self.hare = hare
        for column in columns:
            if column.column_key == _COLUMN_KEY_PRI:
                self.primary_keys.add(column.column_name)
            if column.extra == _COLUMN_AUTOINCREMENT:
                self.auto_incr_key = column.column_name
            self.columns[column.column_name] = column

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def is_column(self, column):
        """check whethere the `column` belongs to this table
        :param column: column name to be checked
        :return: None, if column belongs to this table
                 raises HareException, if if column not belongs to this table
        """
        return column in self.columns

    def truncate(self):
        """truncate this table
        :return:
        """
        sql = u"""TRUNCATE TABLE `{0}`""".format(self.name)
        self.hare.dbi.modify(sql)


class Model(object):

    def __init__(self, **kwds):
        self._data = {}
        # modified columns
        self._modified = set()
        self.set_many(**kwds)

    @classmethod
    def _check_column(cls, column):
        """check whethere the `column` belongs to this table
        :param column: column name to be checked
        :return: None, if column belongs to this table
                 raises HareException, if if column not belongs to this table
        """
        if not cls.table.is_column(column):
            raise HareException("'%s' is not a column of table '%s'" % (
                column, cls.table.name))

    def set_many(self, **kvs):
        if not kvs:
            return self
        for k, v in kvs.items():
            self._check_column(k)
            self.data[k] = v
            self._modified.add(k)
        return self

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        return super(Model, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self.table.columns:
            self._data[key] = value
            self._modified.add(key)
        else:
            super(Model, self).__setattr__(key, value)

    def __delattr__(self, item):
        if item in self.data:
            self.data.popitem(item)
            self._modified.discard(item)
        else:
            super(Model, self).__delattr__(item)

    def __eq__(self, other):
        if not other or not isinstance(other, self.__class__):
            return False
        if self == other:
            return True
        return self.data.__eq__(other.data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        raise HareException("Not allowed")

    def save(self):
        columns = u', '.join(self._modified)
        values = u', '.join([u'%({0})s'.format(k) for k in self._modified])
        sql = u"""INSERT INTO `{table}`({columns})
                  VALUES({values})""".format(
                      table=self.table.name, columns=columns, values=values)
        dbi = self.table.hare.dbi
        dbi.modify(sql, self.data)
        self._modified.clear()
        id_ = dbi.get_insert_id()
        auto_incr_key = self.table.auto_incr_key
        if auto_incr_key:
            self.set_many(**self.get(**{auto_incr_key: id_}).data)
        else:
            self.set_many(**self.get(**{
                key: self.data[key] for key in self.table.primary_keys}).data)
        return id_

    def update(self):
        table = self.table
        if not table.primary_keys:
            raise HareException(u"Table '%s' has not primary key" % self.table)
        conds = []
        for key in table.primary_keys:
            if self.data[key]:
                conds.append(u"{key} = %({key})s".format(key=key))
        if not conds:
            raise HareException(
                u"Primary keys of table '%s' are None value" % self.table)
        slices = [u"{key} = %({key})s".format(
            key=key) for key in self._modified]
        if not slices:
            # log here
            return
        sql = u"""UPDATE `{table}`
                  SET {slices}
                  WHERE {where}""".format(
                      table=table.name, where=' AND '.join(conds),
                      slices=', '.join(slices))
        ret = table.hare.dbi.modify(sql, self.data)
        self._modified.clear()
        return ret

    def delete(self):
        table = self.table
        if not table.primary_keys:
            raise HareException(u"Table '%s' has not primary key" % self.table)
        conds = []
        for key in table.primary_keys:
            if self.data[key]:
                conds.append(u"{key} = %({key})s".format(key=key))
        if not conds:
            raise HareException(
                "Primary keys of table '%s' are None value" % self.table)
        sql = u"""DELETE FROM `{table}`
                  WHERE {where}""".format(
                      table=table.name, where=u' AND '.join(conds))
        return table.hare.dbi.modify(sql, self.data)

    @classmethod
    def get(cls, **kwds):
        rows = cls.select_many(**kwds)
        if not rows:
            return None
        if len(rows) > 1:
            raise HareException(
                'more than one rows found with this query condition')
        obj = cls(**rows[0])
        obj._modified.clear()
        return obj

    @classmethod
    def select_many(cls, cols=None, **kwds):
        table = cls.table
        if not cols:
            cols = table.columns.keys()
        else:
            for col in cols:
                cls._check_column(col)
        conds = [u'1 = 1']
        for k in kwds.keys():
            cls._check_column(k)
            conds.append(u"{key} = %({key})s".format(key=k))
        where = u' AND '.join(conds)
        columns = ', '.join(cols)
        sql = u"""SELECT {columns}
                  FROM `{table}`
                  WHERE {where}""".format(
                      columns=columns, table=table.name, where=where)
        rows = table.hare.dbi.select_many(sql, args=kwds)
        return rows

    @classmethod
    def paginate(cls, ret_columns=None, params=None, page=1, per_page=10,
                 pageable=True):
        """pagination for this table
        :param ret_columns: columns selected
        :param params: query conditions, like: {
                    "column-1": (">=", value-1)
                    "column-2": ("LIKE", value-2)
                    "column-3": ("BETWEEN", (value-3-1, values-3-2)),
                    ...
                },
                legal operators are:
                    {'=', 'LIKE', '>=', '>', '<', '<=', 'IS', 'IN',
                     'BETWEEN', 'IS NOT'},
                case insensitive
        :param page: current page
        :param per_page: page sizes
        :param pageable: whether pagination
        :return: Pagination
        """
        if not ret_columns:
            ret_columns = cls.table.columns.keys()
        else:
            for col in ret_columns:
                cls._check_column(col)
        cols = ', '.join(ret_columns)
        sql = u"""SELECT {0} FROM `{1}`""".format(cols, cls.table.name)
        dbi = cls.table.hare.dbi
        return paginate(dbi, sql, params, page, per_page)
