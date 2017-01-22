import pytest

from . import User, UserRole
from ..hare import HareException


def test_table():
    u = User()
    assert u.table.name == 'user'


def test_data():
    u = User()
    assert not u.data
    u.nickname = 'haha'
    assert u.data['nickname'] == 'haha'


def test_setattr():
    User.table.truncate()
    u = User()
    u.age = 100
    u.nickname = 'oksfsdfsdf'
    u.save()
    assert u.uid > 0


# def test_set_many():
#     u = User()
#     u.set_many(**{'nickname': 'haha', 'email': 'a@q.com'})
#     assert len(u.data) == 2
#     assert 'nickname' in u.data
#     with pytest.raises(HareException):
#         u.set_many(**{'nickname': 'haha', 'not_exists_column': 'a@q.com'})
#
#
# def test_truncate():
#     User.table.truncate()
#     User(**{'nickname': 'hello', 'email': 'xx@qq.com'}).save()
#     assert len(User.select_many()) == 1
#     User.table.truncate()
#     assert len(User.select_many()) == 0
#
#
# def test_save():
#     User.table.truncate()
#     u = User()
#     insert_id = u.set_many(**{'nickname': 'www', 'email': 'abc@ad.com'}).save()
#     assert u.uid == insert_id
#
#
# def test_select_many():
#     # get all rows
#     # each element is an `dict`
#     User.table.truncate()
#     rows = User.select_many()
#     assert len(rows) == 0
#     u = User()
#     u.set_many(**{'nickname': 'www', 'email': 'abc@ad.com'}).save()
#     rows = User.select_many()
#     assert len(rows) == 1
#     assert isinstance(rows[0], dict)
#
#
# def test_update():
#     User.table.truncate()
#     for i in range(10):
#         User(**{'nickname': str(i), 'email': str(i)+'@gmail.com'}).save()
#     rows = User.select_many()
#     for row in rows:
#         user = User(**row)
#         user.nickname *= 2
#         user.update()
#
#     rows = User.select_many()
#     for row in rows:
#         assert len(row['nickname']) == 2
#
#
# def test_delete():
#     User.table.truncate()
#     for i in range(10):
#         User(**{'nickname': str(i), 'email': str(i) + '@gmail.com'}).save()
#     rows = User.select_many()
#     for row in rows:
#         User(**row).delete()
#
#
# def test_paginate():
#     User.table.truncate()
#     for i in range(100):
#         User(**{'nickname': str(i), 'email': str(i) + '@gmail.com'}).save()
#     for i in range(10):
#         pagination = User.paginate(page=i+1, per_page=10)
#         assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(page=1, per_page=100)
#     assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(params={'uid': ('>=', 50)}, page=1, per_page=10)
#     assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(params={'uid': ('>', 10)}, page=1, per_page=10)
#     assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(params={'uid': ('<', 10)}, page=1, per_page=10)
#     assert len(pagination.items) == pagination.per_page - 1
#
#     pagination = User.paginate(params={'uid': ('<=', 10)}, page=1, per_page=10)
#     assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(params={'nickname': ('like', '9')}, page=1, per_page=10)
#     assert len(pagination.items) == pagination.per_page
#
#     pagination = User.paginate(params={'nickname': ('is', None)}, page=1, per_page=10)
#     assert len(pagination.items) == 0
#
#     pagination = User.paginate(params={'nickname': ('is not', None)}, page=1, per_page=10)
#     assert len(pagination.items) == 10
#
#     pagination = User.paginate(params={'nickname': ('  is not  ', None)}, page=1, per_page=10)
#     assert len(pagination.items) == 10
#
#     pagination = User.paginate(params={'nickname': ('like', '999')}, page=1, per_page=10)
#     assert len(pagination.items) == 0