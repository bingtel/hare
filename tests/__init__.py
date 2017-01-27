from __future__ import absolute_import
import pymysql
from hare import Hare, Model


USER_TABLE = """CREATE TABLE `user` (
                  `uid` int(11) NOT NULL AUTO_INCREMENT,
                  `nickname` varchar(20) DEFAULT NULL,
                  `email` varchar(20) DEFAULT NULL,
                  PRIMARY KEY (`uid`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

haredb = Hare(host='localhost', user='root',
              password='135246', db='test',
              charset='utf8',
              cursorclass=pymysql.cursors.DictCursor)


@haredb.table('user')
class User(Model):
    pass


@haredb.table('user_role')
class UserRole(Model):
    pass