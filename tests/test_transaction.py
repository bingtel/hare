import logging
from traceback import format_exc

from . import haredb, User
from ..hare import HareException


def save_user(fail=False):
    user = User().set_many(**{'nickname': 'test'})
    user.save()
    if fail:
        1/0


def test_tx():
    User.table.truncate()
    try:
        haredb.tx(save_user)(True)
    except HareException as he:
        assert True
    except:
        logging.error(format_exc())
    else:
        assert len(User.select_many()) == 0

    haredb.tx(save_user)()
    assert len(User.select_many()) > 0


def test_get_tx():
    User.table.truncate()
    assert len(User.select_many()) == 0

    with haredb.get_tx() as tx:
        try:
            save_user(True)
        except:
            logging.error(format_exc())
            tx.rollback()
        else:
            tx.commit()
    assert len(User.select_many()) == 0

    with haredb.get_tx() as tx:
        try:
            save_user()
        except:
            logging.error(format_exc())
            tx.rollback()
        else:
            tx.commit()
    assert len(User.select_many()) > 0


# def test_nested_transaction():
#     User.table.truncate()
#     assert len(User.select_many()) == 0
#
#     with haredb.get_tx() as tx:
#         try:
#             save_user(True)
#         except:
#             logging.error(format_exc())
#             tx.rollback()
#         else:
#             tx.commit()
#     assert len(User.select_many()) == 0
