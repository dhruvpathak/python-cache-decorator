__author__ = "Dhruv Pathak"


import cPickle
import logging
import time
from functools import wraps
from django.conf import settings
import traceback

"""following imports are from datautils.py in this repo,
https://github.com/dhruvpathak/misc-python-utils/blob/master/datautils.py

datautils also contains many other useful data utility methods/classes
"""

from datautils import mDict, mList, get_nested_ordered_dict, nested_path_get

"""following import is specific to django framework, and can be altered
based on what type of caching library your code uses"""
from django.core.cache import cache, caches


logger = logging.getLogger(__name__)



def cache_result(cache_key=None, cache_kwarg_keys=None, seconds=900, cache_filter=lambda x: True, cache_setup = "default"):
    def set_cache(f):
        @wraps(f)
        def x(*args, **kwargs):
            if settings.USE_CACHE is not True:
                result = f(*args, **kwargs)
                return result
            try:
                # cache_conn should be a cache object supporting get,set methods
                # can be from python-memcached, pylibmc, django, django-redis-cache, django-redis etc
                cache_conn = caches[cache_setup]
            except Exception, e:
                result = f(*args, **kwargs)
                return result
            final_cache_key = generate_cache_key_for_method(f, kwargs, args, cache_kwarg_keys, cache_key)
            try:
                result = cache_conn.get(final_cache_key)
            except Exception, e:
                result = None
                if settings.DEBUG is True:
                    raise
                else:
                    logger.exception("Cache get failed,k::{0},ex::{1},ex::{2}".format(final_cache_key, str(e), traceback.format_exc()))

            if result is not None and cache_filter(result) is False:
                result = None
                logger.debug("Cache had invalid result:{0},not returned".format(result))

            if result is None: # result not in cache
                result = f(*args, **kwargs)
                if isinstance(result, (mDict, mList)):
                    result.ot = int(time.time())
                if cache_filter(result) is True:
                    try:
                        cache_conn.set(final_cache_key, result, seconds)
                    except Exception, e:
                        if settings.DEBUG is True:
                            raise
                        else:
                            logger.exception("Cache set failed,k::{0},ex::{1},ex::{2},dt::{3}".format(final_cache_key, str(e), traceback.format_exc(), str(result)[0:100],))
                #else:
                #    logger.debug("Result :{0} failed,not cached".format(result))

            else: # result was from cache
                if isinstance(result, (mDict, mList)):
                    result.src = "CACHE_{0}".format(cache_setup)
            return result
        return x
    return set_cache


def generate_cache_key_for_method(method, method_kwargs, method_args, cache_kwarg_keys=None, cache_key=None):
    if cache_key is None:
        if cache_kwarg_keys is not None and len(cache_kwarg_keys) > 0:
            if len(method_args) > 0:
                raise Exception("cache_kwarg_keys mode needs set kwargs,args should be empty")

            method_kwargs = get_nested_ordered_dict(method_kwargs)
            cache_kwarg_values = [nested_path_get(method_kwargs, path_str=kwarg_key, strict=False) for kwarg_key in cache_kwarg_keys]
            if any([kwarg_value is not None for kwarg_value in cache_kwarg_values]) is False:
                raise Exception("all cache kwarg keys values are not set")

            final_cache_key = "{0}::{1}::{2}".format(str(method.__module__), str(method.__name__), hash(cPickle.dumps(cache_kwarg_values)))
        else:
            final_cache_key = "{0}::{1}".format(str(method.__module__), str(method.__name__))
            final_cache_key += "::{0}".format(str(hash(cPickle.dumps(method_args, 0)))) if len(method_args) > 0 else ''
            final_cache_key += "::{0}".format(str(hash(cPickle.dumps(method_kwargs, 0)))) if len(method_kwargs) > 0 else ''
    else:
        final_cache_key = "{0}::{1}::{2}".format(method.__module__, method.__name__, cache_key)

    return final_cache_key

