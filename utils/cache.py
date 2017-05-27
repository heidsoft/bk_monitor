# -*- coding: utf-8 -*-

import copy
import functools
import time

from django.conf import settings
from django.core.cache import cache

from common.log import logger
from utils.request_middlewares import get_request


class InstanceCache(object):

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.__cache = {}
        # 每小时清空过期key释放内存
        self.clear_expires_interval = 60*60

    def clear(self):
        self.__cache = {}

    def clear_expires(self):
        def _clear_expires():
            for k in self.__cache.keys():
                if k == clear_key:
                    continue
                self.delete(k)
            return copy.copy(self.__cache)

        # 保留key，用于记录最近一次清除过期key的时间
        clear_key = "%s:last_clear_time" % str(self)
        last_clear_time = self.__cache.get(clear_key)
        if last_clear_time:
            last_clear_time = last_clear_time[0]
        if ((last_clear_time is None or time.time() - last_clear_time) >
            self.clear_expires_interval):
            self.set(clear_key, time.time())
            self.__cache = _clear_expires()

    def set(self, key, value, seconds=0):
        self.__cache[key] = (value, time.time() + seconds if seconds else 0)

    def get(self, key):
        self.clear_expires()
        value = self.__cache.get(key)
        if not value:
            return None
        if value[1] and time.time() > value[1]:
            del self.__cache[key]
            return None
        return value[0]

    def delete(self, key):
        try:
            del self.__cache[key]
        except:
            pass


instance_cache = InstanceCache()


class web_cache(object):

    def __init__(self, time_out=60*60*24, db_cache=True):
        self.time_out = time_out
        self.db_cache = db_cache

    def _cache_key(self, func_name, args, kwargs):
        # 新增根据用户openid设置缓存key
        try:
            username = get_request().user.username
        except:
            username = "backend"
        return 'cache.%s:%s,%s[%s]' % (
            func_name,
            to_sorted_str(args),
            to_sorted_str(kwargs),
            username
        )

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            if settings.RUN_MODE == "DEVELOP":
                return task_definition(*args, **kwargs)

            cache_key = self._cache_key(
                task_definition.func_name, args, kwargs)

            # 从内存读取缓存
            return_value = instance_cache.get(cache_key)
            if return_value:
                return return_value

            # 从DB读取缓存
            if self.db_cache:
                return_value = cache.get(cache_key)
            if return_value is None:
                return_value = self._call(task_definition, args, kwargs)
                logger.debug("Cache miss: %s" % cache_key)
            else:
                logger.debug("Cache hit: %s" % cache_key)

            instance_cache.set(cache_key, return_value, self.time_out)
            return return_value
        return wrapper

    def _call(self, task_definition, args, kwargs):

        cache_key = self._cache_key(task_definition.func_name, args, kwargs)

        logger.debug(u"Cache CALL %s" % cache_key)

        # 执行真实函数
        return_value = task_definition(*args, **kwargs)
        if self.db_cache:
            # 记录缓存
            try:
                cache.set(cache_key, return_value, self.time_out)
            except Exception, e:
                # 缓存出错不影响主流程
                logger.exception(u"存缓存时报错：{}".format(e))

        return return_value


class lazy_property(object):

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(obj):
            cache_key = lazy_property.gen_cache_key(obj, task_definition.func_name)

            # 读取缓存
            return_value = getattr(obj, cache_key, None)
            if not return_value:
                return_value = task_definition(obj)
                setattr(obj, cache_key, return_value)
            return return_value
        return wrapper

    @staticmethod
    def gen_cache_key(obj, func_name):
        return "%s(%s)_%s" % (
            obj.__class__.__name__, id(obj), func_name
        )


def to_sorted_str(params):
    """
    对于用字典作为关键的时候，该方法能够一定程度保证前后计算出来的key一致
    :param params:
    :return:
    """
    if isinstance(params, dict):
        data = [(key, params[key]) for key in sorted(params.keys())]
        s = u""
        for k, v in data:
            s += u"-%s:%s" % (k, to_sorted_str(v))
        return s
    elif isinstance(params, list) or isinstance(params, tuple):
        data = map(lambda x: to_sorted_str(x), params)
        return u"[%s]" % (u",".join(data))
    else:
        return u"%s" % params
