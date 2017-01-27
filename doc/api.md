Hare API-0.1
===============

## Hare Object

### name

数据库的名称，string

### dbi

获取一个连接。

如果获取``dbi``时，处于事务上下文中，则返回：

    和事务相同的连接

如果获取``dbi``时，不处于事务上下文中， 则返回：

    一个新的连接
    
### table(f, table_name=None)

装饰器， 用于绑定数据库表和Model类之间的映射关系，如：

    @haredb.table('table')
    class Tbl(Model):
        pass

### tables()

返回该数据库下的表名称列表，list;

### get_tx()

获取一个新的事务


### tx(f)

事务装饰器, 保证函数``f``中使用的是同一个数据库连接

## Model Object

class hare.**Model**(**kwds)

### table
该Model对应的表对象，具有下列属性：

名称 | 类型 | 用途
----|------|----
auto_incr_key | string | 该表的自增主键;表没有自增主键时，为``None``
columns | OrderedDict | 该表的所有字段， key是字段名称，value是对应的``Column``对象;使用``columns``.keys()来获取所有的字段名称(字段的顺序按照sql中声明的顺序)
hare | Hare对象 | 该表所属的数据库
name | string  | 该表的名称
primary_keys | string set | 该表的主键名称集合

方法      | 类型    |    描述
----------|----------|------------
is_column(column)| 实例方法 | 检查column是否属于表, 返回True/False；
truncate() | 实例方法 | 清空该表的数据

### data

Model对象的数据，是一个dict，存放字段和对应的值；``data``中的值，可以直接通过'.'的方式来获取Model对象的column_name的值

### set_many(**kwds)

设置Model对象的字段的值

### save()

保存新建的Model对象；如果Model对应的表定义了自增主键，可以通过：

    model.自增主键
    
的方法获得生成的主键值

### get(**kwds)

根据字段的值,筛选出一个Model对象；如果数据库表中含有多条，会抛出``HareException``异常。

### update()

使用：

    set_many(**kwds)
    
或者：

    model.column = val

的方式更改Model对象的值后，然后调用``update()``来更新数据库记录。

### delete()

从数据库中删除掉Model对象对应的记录。

### select_many(**kwds)

根据column过滤，返回一个或者多个记录.

### paginate(ret_columns=None, params=None, page=1, per_page=10)

单表分页， 根据params筛选出符合条件的值

名称 | 类型 | 用途
----|------|----
ret_columns | string list | 希望返回的主键列表，为None时，返回所有的字段
params | dict | 查询条件，如：{"column-1": (">=", value-1),"column-2": ("LIKE", value-2),"column-3": ("BETWEEN", (value-3-1, values-3-2)),               ...   }， 合法的操作符是： {'=', 'LIKE', '>=', '>', '<', '<=', 'IS', 'IN', 'BETWEEN', 'IS NOT'}
page | int | 

## hare.Connection

方法      | 类型    |    描述
----------|----------|------------
autocommit(autocommit)| 实例方法 | 修改数据库连接的``autocommit``属性
select| 实例方法 | 返回一条记录，dict
select_many(sql, args=None) | 实例方法 | 返回多条记录，每个记录是个dict
modify(sql, args=None) | 实例方法 | 修改记录
modify_many(sql, args) | 实例方法 | 批量操作
commit() | 实例方法 | 提交事务
rollback() | 实例方法 | 回滚事务
ping() | 实例方法 | 测试连接是否可用
get_insert_id() | 实例方法 | 执行插入后，返回的自增主键值
close() | 实例方法 | 关闭连接


## hare.Transaction

事务，实现了上下文管理，即支持``with``操作。

方法      | 类型    |    描述
----------|----------|------------
is_finished()| 实例方法 | 事务是否已经完成(调用过comit()/rollback())
commit() | 实例方法 | 提交事务
rollback() | 实例方法 | 回滚事务


## Others

### HareException

    异常类

### paginate(dbi, sql, params=None, page=-1, per_page=10)
分页查询函数， 其中：

    dbi: 数据库连接
    sql: 要执行的sql
    params: 查询条件, 比如: {
            "column-1": (">=", value-1)
            "column-2": ("LIKE", value-2)
            "column-3": ("BETWEEN", (value-3-1, values-3-2)),
            ...
        },
        合法的操作符有:
            {'=', 'LIKE', '>=', '>', '<', '<=', 'IS', 'IN',
             'BETWEEN', 'IS NOT'},
        大小写无关
    page: 当前页
    per_page: 每页的条数
    return: 一个Pagination对象

### Pagination
分页对象，含有：

#### items
记录，list， 每个元素是dict

#### pages
总页数

#### page
当前页

#### total
总的结果数

#### per_page
每页的条数
