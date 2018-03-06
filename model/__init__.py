import time

from pymongo import *

# mongo 数据库的名字
mongodb_name = 'SeleniumPython'
client = MongoClient("mongodb://10.9.36.125:27017")
mongodb = client[mongodb_name]


def timestamp():
    return int(time.time())


def next_id(name):
    """
    用来给 mongo 的数据生成一个 自增的数字 id
    """
    query = {
        'name': name,
    }
    update = {
        '$inc': {
            'seq': 1
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    # 存储数据的 id 是放在一个叫做 data_id 的表里面
    # upsert 设置为 True, 如果没有数据表，就创建该新表。
    doc = mongodb['data_id']
    # find_and_modify 是一个原子操作函数, 所以可以保证不会生成重复的 id
    new_id = doc.find_and_modify(**kwargs).get('seq')
    return new_id


class Mongo(object):
    @classmethod
    def _fields(cls):
        fields = [
            '_id',
            # (字段名, 类型, 值)
            ('id', int, -1),
        ]
        return fields

    @classmethod
    def has(cls, **kwargs):
        """
        检查一个元素是否在数据库中
        """
        return cls.find_one(**kwargs) is not None

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(class_name, '\n  '.join(properties))

    @classmethod
    def new(cls, form=None, **kwargs):
        """
        new 是给外部使用的函数， 用于创建并保存新数据
        new 是自动 save 的, 所以使用后不需要 save
        """
        name = cls.__name__
        # 创建一个空对象
        m = cls()
        # 把定义的数据写入空对象, 未定义的数据输出错误
        fields = cls._fields()
        # 去掉 _id 这个特殊的字段
        fields.remove('_id')
        if form is None:
            form = {}
        # 给属性赋值
        for f in fields:
            k, t, v = f
            if k in form:
                setattr(m, k, t(form[k]))
            else:
                # 设置默认值
                setattr(m, k, v)
        # 处理额外的参数 kwargs
        for k, v in kwargs.items():
            if hasattr(m, k):
                setattr(m, k, v)
            else:
                raise KeyError
        # 写入默认数据
        m.id = next_id(name)
        m.save()
        return m

    @classmethod
    def _new_with_bson(cls, bson):
        """
        这是给内部 all 这种函数使用的函数
        从 mongo 数据中恢复一个 model
        """
        m = cls()
        fields = cls._fields()
        # 去掉 _id 这个特殊的字段
        fields.remove('_id')
        for f in fields:
            k, t, v = f
            if k in bson:
                setattr(m, k, bson[k])
            else:
                # 设置默认值
                setattr(m, k, v)
        # 这一句必不可少，否则 bson 生成一个新的_id
        setattr(m, '_id', bson['_id'])
        return m

    @classmethod
    def count(cls, query):
        name = cls.__name__
        return mongodb[name].find(query).count()

    @classmethod
    def find(cls, query, skip=0, limit=0, sort=None):
        name = cls.__name__
        if not sort:
            sort = [('id', 1)]
        ds = mongodb[name].find(query).skip(skip).limit(limit).sort(sort)
        l = [cls._new_with_bson(d) for d in ds]
        return l

    @classmethod
    def find_one(cls, query):
        """
        和 find 一样， 但是只返回第一个元素
        找不到就返回 None
        """
        l = cls.find(query)
        if len(l) > 0:
            return l[0]
        else:
            return None

    def save(self):
        '''
        保存数据到 mongo
        '''
        name = self.__class__.__name__
        mongodb[name].save(self.__dict__)

    @classmethod
    def delete(cls, id):
        name = cls.__name__
        query = {
            'id': int(id),
        }
        mongodb[name].delete_one(query)

    @classmethod
    def update(cls, query, form):
        name = cls.__name__
        mongodb[name].update(query, form)

    @classmethod
    def update_all(cls, query, form):
        name = cls.__name__
        mongodb[name].update_many(query, form)

    def json(self):
        """
        json 函数返回 model 的 json 字典
        子元素可以覆盖这个方法
        """
        _dict = self.__dict__
        d = {k: v for k, v in _dict.items() if k not in self.blacklist()}
        return d

    def blacklist(self):
        """
        这是给 json 函数用的
        因为返回 json 格式数据的时候
        我们有时候不希望所有字段都返回
        比如 _id
        """
        b = [
            '_id',
            'id',
        ]
        return b

    @staticmethod
    def drop_data_id():
        name = 'data_id'
        mongodb[name].drop()

    @classmethod
    def drop(cls):
        name = cls.__name__
        mongodb[name].drop()
