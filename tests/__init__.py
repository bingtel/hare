from __future__ import absolute_import
import logging
from hare import Hare

logger = logging.getLogger('hare')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


USER_TABLE = """CREATE TABLE `user` (
                  `uid` int(11) NOT NULL AUTO_INCREMENT,
                  `nickname` varchar(20) DEFAULT NULL,
                  `email` varchar(20) DEFAULT NULL,
                  PRIMARY KEY (`uid`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

haredb = Hare(host='localhost', user='root',
              password='135246', db='test',
              charset='utf8', logger=logger)


@haredb.table('user')
class User(haredb.Model):
    pass


@haredb.table('user_role')
class UserRole(haredb.Model):
    pass