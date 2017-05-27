# -*- coding: utf-8 -*-
__author__ = u"蓝鲸智云"
__copyright__ = "Copyright (c) 2012-2017 Tencent BlueKing. All Rights Reserved."

import re
import arrow
import socket
import random
import hashlib
import itertools


def is_ip(ci_name):
    try:
        socket.inet_aton(ci_name)
        return True
    except:
        return False


def get_local_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.

    stackoverflow上有人说用socket.gethostbyname(socket.getfqdn())
    但实测后发现有些机器会返回127.0.0.1
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def get_first(objs, default=""):
    """get the first element in a list or get blank"""
    if len(objs) > 0:
        return objs[0]
    return default


def get_list(obj):
    return obj if isinstance(obj, list) else [obj]


def split_list(raw_string):
    if isinstance(raw_string, (list, set)):
        return raw_string
    re_obj = re.compile(r'\s*[;,]\s*')
    return filter(lambda x: x, re_obj.split(raw_string))


def expand_list(obj_list):
    return list(itertools.chain.from_iterable(obj_list))


def remove_blank(objs):
    if isinstance(objs, (list, set)):
        return [unicode(obj) for obj in objs if obj]
    return objs


def remove_tag(text):
    """去除 html 标签"""
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)


def get_random_id():
    return "%s%s" % (arrow.now().timestamp, random.randint(1000, 9999))


def _count_md5(content):
    if content is None:
        return None
    m2 = hashlib.md5()
    if isinstance(content, unicode):
        m2.update(content.encode("utf8"))
    else:
        m2.update(content)
    return m2.hexdigest()


def get_md5(content):
    if isinstance(content, list):
        return [_count_md5(c) for c in content]
    else:
        return _count_md5(content)
