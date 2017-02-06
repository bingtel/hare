# -*- coding: utf-8 -*-

from .exception import HareException


class Pagination(object):
    def __init__(self, items, pages, page, per_page, total):
        self.items = items
        self.pages = pages
        self.page = page
        self.total = total
        self.per_page = per_page

    def __str__(self):
        return (u"Pagination<pages: {0.pages}, page: {0.page}, "
                "total: {0.total}, per_page: {0.per_page}, "
                "items: {0.items}>".format(self))


_LEGAL_OPS = {'=', 'LIKE', '>=', '>', '<', '<=', 'IS', 'IN',
              'BETWEEN', 'IS NOT'}


def _check_in(params):
    if not params:
        raise HareException("params for 'IN' can not be empty")


def _check_between(params):
    if not (params and len(params) == 2):
        raise HareException(
            "there should be two params for 'BETWEEN' and 'AND'")

_VALIDATORS = {
    'IN': _check_in,
    'BETWEEN': _check_between
}


def paginate(dbi, sql, params=None, page=-1, per_page=10):
    """pagination query
    :param dbi: connection
    :param sql:
    :param params: query condition, like: {
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
    :param per_page: number for queried rows
    :return: Pagination
    """
    if per_page < 0 or page < 0:
        raise HareException('page_size or cur_page can not be minus')
    kvs = {}
    if not params:
        cnt_sql = u"""SELECT COUNT(*) AS cnt
                      FROM ({0}) AS T""".format(sql)
        cnt = dbi.select(cnt_sql)['cnt']
    else:
        conds = []
        for k, v in params.items():
            op, val = v
            if not op:
                raise HareException("operator can not be None")
            op = op.strip().upper()
            if op not in _LEGAL_OPS:
                raise HareException(
                    "operator should be one of %s" % ', '.join(_LEGAL_OPS))
            validator = _VALIDATORS.get(op)
            if validator:
                validator(val)
            if op == 'IN':
                elements = []
                for i, e in enumerate(val):
                    tmp_key = u'%({0}-{1})s'.format(k, i)
                    elements.append([u'%({0})s'.format(tmp_key)])
                    kvs[tmp_key] = e
                conds.append(u"{0} IN ({1})".format(k, ', '.join(elements)))
            elif op == 'BETWEEN':
                kvs[u"{0}-1".format(k)] = val[0]
                kvs[u"{0}-2".format(k)] = val[-1]
                conds.append(u'{0} BETWEEN %({0}-1)s AND %({0}-2)s'.format(k))
            elif op == 'LIKE':
                kvs[k] = u"%{0}%".format(val)
                conds.append(u"{0} LIKE %({0})s".format(k))
            else:
                kvs[k] = val
                conds.append(u'{0} {1} %({0})s'.format(k, op))
        slices = u' AND '.join(conds)
        cnt_sql = u"""SELECT COUNT(*) AS cnt
                      FROM ({0} WHERE {1}) AS T""".format(sql, slices)
        sql = u"{0} WHERE {1}".format(sql, slices)
        cnt = dbi.select(cnt_sql, kvs)['cnt']
    if not cnt or not per_page:
        return Pagination([], 0, page, per_page, 0)
    limit = (page - 1) * per_page
    query_sql = u'{0} LIMIT {1}, {2}'.format(sql, limit, per_page)
    rows = dbi.select_many(query_sql, kvs if params else None)
    pages = cnt / per_page if not cnt % per_page else cnt / per_page + 1
    return Pagination(rows, pages, page, per_page, cnt)
