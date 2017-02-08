Hare
=====================

``hare``是一个基于pymysql并运用ActiveRecord模式的ORM框架, 在虚拟环境下，通过：

	pip install hare
	
即可安装。

当前，它只支持：

	MySQL

## 动机
在Python下进行数据库操作， 大体有两种方法：

    1、使用raw sql
    2、使用ORM

### Raw SQL
python中常用的``raw sql``工具是：

    MySQLdb
    PyMySQL

使用``raw sql``的好处是：

    给予开发人员极大的自由，让开发人员知道具体要执行的sql，方便sql优化

坏处是``麻烦``：

    写起来麻烦、影响开发速度；维护起来也麻烦

### ORM
python中用的最广的ORM是``SQLAlchemy``和``Peewee``.

使用``ORM``的好处是：

    写起来方便，维护方便

坏处是：

    对开发人员透明、不利于sql优化；
    主流的ORM学习成本高，对于一般的中小型项目而言，用不到那么到功能，如SQLAlchemy

此外， python``ORM``框架的使用哲学是：

    需要要手动的在类中配置字段和对应类型， 然后使用ORM去自动创建对应的table。

而开发人员的哲学是:

    手动使用sql建表、然后再去创建对应的ORM。

那么， 比较下来，就产生了新的需求： 实现一个``ORM``，满足下列要求：

    1、方便ORM和数据库表之间的映射、最好不用在ORM中声明字段
    2、支持raw sql
    3、不需要实现复杂的API(太复杂的，可以直接通过raw sql实现)
    4、支持事务(声明式、命令式)

很容易想到， 使用``Active Record``的方式实现一个ORM，满足上述条件

于是就实现了一个名为``Hare``的ORM.``Hare``的意思是``野兔``， 希望进行python的db操作时，像兔子一样快。

### 参考框架

在设计和实现``Hare``的过程中，参考了``Flask``框架和``jFinal``框架的设计。

#### jFinal

jFinal是一种轻量的java web框架；设计和实现``Hare``的过程中，借鉴了它的一些设计思想：

##### 自动获取表结构

jFinal在启动的时候，根据ORM对应的表名，通过``MySQL``的``INFORMATION_SCHEMA``取获取表结构；
``Hare``也通过此方式来获取。

#### Flask

Flask是一种轻量的python web框架；设计和实现``Hare``的过程中，借鉴了它的一些设计思想：

##### 将框架对象化
flask中，通过：

    app = Flask(__name__)

的方式来建立一个应用对象， 并在该对象中存储相关路由、处理器等信息；

Hare中， 采用类似方式，通过：

    haredb = Hare(host='localhost', user='root',
              password='*****', db='test',
              charset='utf8')

来创建一个数据源对象， 存放数据操作所需的一切信息。
##### 装饰器
flask中，使用装饰器的方式，来定义路由处理：

    @app.route('/home', methods=['GET'])
    def home():
        pass

Hare也使用装饰器来定义定义数据模型类和表之间的映射关系，并存储， 如下：

    @haredb.table('user')
    class User(Model):
        pass

把``User``类和``user``表对应起来.

同时，Hare中的事务也可以通过装饰器来实现：

    @haredb.tx
    def func(...):
        ...

## 使用
数据库的"库->表->字段"，是一种层次分明的结构。``Hare``也基于此。

用户提供数据库的连接配置，就对应了一个数据源，也就是Database；

	haredb = Hare(
	        host='localhost', user='root',
	        password='********', db='test',
	        charset='utf8')

假设在``test``数据库中已经创建了一个``user``表：

    USER_TABLE = """CREATE TABLE `user` (
                  `uid` int(11) NOT NULL AUTO_INCREMENT,
                  `nickname` varchar(20) DEFAULT NULL,
                  `email` varchar(20) DEFAULT NULL,
                  PRIMARY KEY (`uid`)
                ) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8"""

通过``装饰器``来声明这个数据库下有哪些表(添加一个名是``user``的table，对应的模型是``User``)：

    @haredb.table('user')
    class User(Model):
        pass

那么:

### 完整的用例如下
```
#! -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from traceback import format_exc
import pymysql
from hare import Hare, Model

# 创建一个Hare对象, 作为数据源
# 会使用默认的logger来记录执行的sql
haredb = Hare(
    host='localhost', user='root',
    password='********', db='test',
    charset='utf8')
    
# 创建一个自定义logger的数据源
logger = logging.getLogger('hare')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
haredb = Hare(
    host='localhost', user='root',
    password='********', db='test',
    charset='utf8',
    logger=logger)

# 将user表和User类绑定
@haredb.table('user')
class User(Model):
    pass
    
# 获取所有的表名
# 返回['user']
print haredb.tables

 
# 获取User类对应的table对象
table = User.table

# 输出表名称
print table.name

# 清空User表
table.truncate()

# 判断字段是否属于该表
print table.is_column('uid')
print table.is_column('uid_not_exists')

# 新建一条记录
u = User()
u.set_many(**{'nickname': 'haha', 'email': 'a@q.com'}).save()

# 获取主键
print u.uid

# 获取一条记录
u = User.get(uid=1)

# 修改字段的值
u.nickname = 'new name'
u.update()

# 删除该对象
u.delete()

# 获取所有的用户记录
# 每个元素是个dict
users = User.select_many()

# 查询符合条件的所有记录
# 每个元素是个dict
users = User.select_many(email='a@q.com')

# 分页查询User表
pagination = User.paginate(params={'nickname': ('is not', None)}, page=1, per_page=10)
print pagination.items

# 获取一条数据库连接
dbi = haredb.dbi

# 执行row sql
# 一条记录
users = dbi.select(u'SELECT * FROM user WHERE uid = 10')
# 多条记录
users = dbi.select_many(u'SELECT * FROM user WHERE uid > 10')
# 执行写操作
dbi.modify(u'DELETE FROM user WHERE uid = %s', 1)
# 批量写操作
rows = [{'nickname': 'test', 'email': 'test@qq.com'}]
dbi.modify_many(u'INSERT INTO user(nickname, email) VALUES(%(nickname)s, %(email)s)', rows)

# 执行事务
@haredb.tx
def save_user():
    user = User().set_many(**{'nickname': 'test2'})
    user.save()
    # 1/0 取消注释该行，则保存失败
    
# 执行事务的另外一种方式
def save_user2():
    user = User().set_many(**{'nickname': 'test2'})
    user.save()
    # 1/0 取消注释该行，则保存失败

with haredb.get_tx() as tx:
    try:
        save_user2()
    except:
        logging.error(format_exc())
        tx.rollback()
    else:
        tx.commit()
print User.select_many()
```
## API

见

	doc/api.md
	
## 个人博客

[bingtel-木犹如此](http://www.bingtel.wang/)