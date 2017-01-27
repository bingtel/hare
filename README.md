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
              charset='utf8',
              cursorclass=pymysql.cursors.DictCursor)

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
              	password='135246', db='test',
              	charset='utf8',
              	cursorclass=pymysql.cursors.DictCursor)

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

#### 1. 添加记录
创建一个User对象并保存：

    u = User()
    u.set_many(**{'nickanem': 'xxxx', 'email': 'xxxx@xx.com'}).save()
    print u.uid

或者：

    u = User(**{'nickanem': 'xxxx', 'email': 'xxxx@xx.com'})
    u.save()
    print u.uid
    
使用事务：

	with haredb.get_tx() as tx:
		try:
			 save_user(...)
		except:
			logging.error(format_exc())
			tx.rollback()
		else:
			tx.commit()

 使用事务装饰器：	
 
 	@haredb.tx
 	def save_user(...):
 		pass


#### 2. 获取一条记录

    u = User.get(uid=1)
    print u.nickname, u.email, u.uid

#### 3. 更新:

    u = User.get(uid=1)
    u.email = 'ooooo@qq.com'
    u.update()
    
或者：

    u = User.get(uid=1)
    u.set_many(**{'email': 'ooooo@qq.com'})
    u.update()

#### 4. 删除对象

    u.delete()

#### 5. 查询多条记录

    # 每个元素是个dict
    users = User.select_many(nickname='xxxx', email='xxx')
    
#### 6. 执行raw sql

	sql = """...."""
	# 返回最多一个结果
	haredb.dbi.select(sql, (...))
	# 返回一个或多个结果
	haredb.dbi.select_many(sql, (...))
	# 执行delete、update等
	haredb.dbi.modify(sql, (...))
	# 执行批量插入等
	haredb.dbi.modify_many(sql, (...))

#### 7. 分页:

    # 获取nickname中包含9的第一页的10条记录
    # 每个元素是个dict
    pagination = User.paginate(params={'nickname': ('like', '9')}, page=1, per_page=10)
    
也可以直接调用``paginate(...)``：

	from hare import paginate
	
	sql = """...."""
	# 模糊匹配"abc"的的列
	params = {"column-name":  ("LIKE", "abc")}

	pagination = paginate(haredb.dbi, sql, params,  1, 10)
	
## API

见

	doc/api.md