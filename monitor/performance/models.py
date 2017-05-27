# -*- coding: utf-8 -*-
"""
@desc:
"""
import datetime
import json
from collections import defaultdict
from urlparse import urljoin

import arrow
from django.conf import settings

from common.mymako import DictObj
from monitor.constants import JA_API, SQL_MAX_LIMIT, AGENT_STATUS
from monitor.errors import (JAAPIError, JAItemDoseNotExists,
                            TableNotExistException, SqlQueryException)
from utils.cache import lazy_property, web_cache
from utils.common_utils import (base_hostindex_id_to_page_id, check_permission,
                                host_key, ignored, is_base_hostindex,
                                page_id_to_base_hostindex_id, parse_host_id,
                                plat_id_cc_to_gse, plat_id_gse_to_cc, safe_int)
from utils.dataview_tools import get_default_time_range, make_where_list, query
from utils.query_cc import CCBiz, get_nick_by_uin
from utils.requests_utils import requests_get, requests_post


class Host(DictObj):
    """主机状态信息实例化
    """

    def __init__(self, kwargs):
        self.id = host_key(kwargs)
        super(Host, self).__init__(kwargs)

    def __getattr__(self, item):
        return u"未知"

    def __str__(self):
        return self.id

    @staticmethod
    def get_agent_status_by_hostid(cc_biz_id, host_ids):
        """获取agent状态信息
        agent状态详细分成4个状态：正常，离线，未安装。已安装，无数据。
        """
        agent_status_info = CCBiz.agent_status(
            cc_biz_id, host_ids
        )
        if not hasattr(host_ids, "__iter__"):
            host_ids = [host_ids]
        for host_id in host_ids:
            agent_status = agent_status_info.get(
                host_id, AGENT_STATUS.UNKNOWN
            )
            # 如果agent在线，检查最近上报是否有数据
            if agent_status == AGENT_STATUS.ON:
                # 只要有任何性能指标有数据，则状态依旧为ON
                try:
                    report_info = HostIndex.data_report_info(cc_biz_id, [host_id])
                    agent_status = (AGENT_STATUS.ON if report_info.get(host_id)
                                    else AGENT_STATUS.NO_DATA)
                except SqlQueryException:
                    agent_status = AGENT_STATUS.UNKNOWN
            agent_status_info[host_id] = agent_status
        return agent_status_info


class ApiModelBase(type):
    """
    django models 迁移至 api models
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ApiModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ApiModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        # Create the class.
        new_class = super_new(cls, name, bases, attrs)
        new_class.objects = new_class
        return new_class


class ApiModel(DictObj):
    # 基础告警指标列表
    action = ""

    __metaclass__ = ApiModelBase

    @classmethod
    def get_url(cls, pk=""):
        bpath = urljoin(JA_API, cls.action)
        if not bpath.endswith("/"):
            bpath += "/"
        if safe_int(pk):
            bpath = urljoin(bpath, '%s/' % pk)
        return bpath

    @classmethod
    def filter(cls, **kwargs):
        assert cls.action != "", u"api url not set"
        res = requests_get(cls.get_url(), **kwargs)
        item_list = cls.parse_api_response(res)
        return [cls(item) for item in item_list]

    @classmethod
    def get(cls, **kwargs):
        if 'id' in kwargs or 'pk' in kwargs:
            pk = kwargs.get("id") or kwargs.get("pk")
            assert pk, u"id is required"
            res = requests_get(cls.get_url(pk=pk))
            if not res.get("data"):
                raise JAItemDoseNotExists(u"[%s] %s" % (
                    cls.__name__, res.get("message")
                ))
            return cls(cls.parse_api_response(res))
        else:
            data = cls.filter(**kwargs)
            if data:
                return data[0]
            else:
                raise JAItemDoseNotExists(
                    u"[%s] no item return" % cls.__name__
                )

    def delete(self, **kwargs):
        # 抛出异常表示删除失败
        cls = self.__class__
        obj_list = self.__class__.filter(**kwargs) if kwargs else [self]
        for obj in obj_list:
            obj_id = obj.id
            if not obj_id:
                raise AttributeError(
                    u"[%s] does not have property: id" % cls.__name__
                )
            base_url = cls.get_url(pk=obj_id)
            url = urljoin(base_url, "delete/")
            res = requests_post(url)
            from monitor.operation_records import post_delete_models
            post_delete_models(sender=cls, instance=obj)
            from monitor.models import CallMethodRecord
            CallMethodRecord.objects.create(
                action=cls.action, url=url, method="DELETE",
                param=json.dumps('{}'), result=res)
            return cls.parse_api_response(res)

    def update(self, **kwargs):
        cls = self.__class__
        url = cls.get_url(pk=self.id)
        from monitor.operation_records import pre_save_models, post_save_models
        pre_save_models(sender=cls, instance=self)
        res = requests_post(url, **kwargs)
        post_save_models(sender=cls, instance=cls(cls.parse_api_response(res)), created=False)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=url, method="POST",
            param=json.dumps(kwargs), result=res)
        return cls(cls.parse_api_response(res))


    @classmethod
    def parse_api_response(cls, result):
        if result["result"]:
            return result["data"]
        else:
            error_message = u"[%s] %s" % (cls.__name__, result["message"])
            if result.get("request_id"):
                error_message += u"\nrequest_id: %s" % result["request_id"]
            raise JAAPIError(
                error_message
            )


    def get_title(self):
        return ''

    def gen_operate_desc(self, operate, ori_data=False):
        """
        根据操作类型，与变更前后的配置生成操作说明
        :param operate: 操作类型：create/update/delete
        :param ori_data: 操作前的配置信息 [可选]
        :return: operate_desc 变更说明
        """
        op_desc = self.get_title()
        if operate in ['create', 'delete']:
            return op_desc
        elif operate == 'update':
            if not ori_data:
                return op_desc
            # 获得2次修改之间， 变更了哪些配置
            changed_config = self.get_operate_changed_config(ori_data)
            # 根据变更的配置， 生成对应的wording
            op_desc = self.gen_op_desc_by_changed_config(changed_config)
        return op_desc

    def get_operate_changed_config(self, ori_data):
        return {}

    def gen_op_desc_by_changed_config(self, changed):
        return self.get_title()

class HostIndex(ApiModel):
    action = "monitor/performance_monitor_items"

    category = ""
    CATEGORY_CHOICES = (
        ("cpu", u"CPU"),
        ("net", u"网络"),
        ("mem", u"内存"),
        ("disk", u"磁盘"),
        ("process", u"进程"),
    )

    @classmethod
    @web_cache(60 * 60)
    def get(cls, **kwargs):
        # 性能指标数据变更不频繁，可以长期缓存
        return super(HostIndex, cls).get(**kwargs)

    @classmethod
    @web_cache(60 * 60)
    def filter(cls, **kwargs):
        return super(HostIndex, cls).filter(**kwargs)

    def get_category_display(self):
        for category_info in self.CATEGORY_CHOICES:
            if self.category == category_info[0]:
                return category_info[1]
            return self.category

    @classmethod
    def get_host_performance_async(cls, args):
        return cls.get_host_performance(*args)

    @classmethod
    def get_host_performance(cls, cc_biz_id, item, category, result_table_id,
                             host_id=None):
        # 获取主机性能信息
        hostindex = cls.get(
            item=item, category=category, result_table_id=result_table_id
        )
        performance_client = BasePerformanceClient(cc_biz_id, hostindex)
        return performance_client.performance_points(host_id=host_id)

    @staticmethod
    @web_cache(60)
    def get_eth_info_by_biz(cc_biz_id):
        """
        获取业务下各机器对应的网卡信息
        """
        from utils.trt import trans_bkcloud_rt_bizid
        rt_id = trans_bkcloud_rt_bizid("%s_%s" % (cc_biz_id, "ja_gse_net_detail"))
        filter_dict = {}
        time_range = get_default_time_range(1, 0)
        filter_dict['thedate__gte'], filter_dict['thedate__lt'] = map(
            lambda x: x.strftime("%Y%m%d"), time_range
        )
        where_sql = " where " if filter_dict else ""
        where_list = make_where_list(filter_dict)
        where_sql += u" and ".join(where_list)
        field_str = u"ip, cloud_id, name"
        sql = "select %s from %s %s group by %s limit 0, 1000" % (
            field_str, rt_id, where_sql, field_str
        )
        data = list()
        with ignored(Exception):
            ret = query(sql)
            data = ret["list"]
        eth_info = {}
        for point in data:
            ip, plat_id = point["ip"], point["cloud_id"]
            plat_id = plat_id_gse_to_cc(plat_id)
            host_id = host_key(ip=ip, plat_id=plat_id)
            eth_name = point["name"]
            if not eth_name.strip().startswith("eth"):
                continue
            eth_info.setdefault(host_id, []).append(eth_name)
        return eth_info

    @staticmethod
    def get_bp_graph_index():
        # 获取需要展示的性能指标
        index_info = defaultdict(list)
        indexs = HostIndex.filter(graph_show=True)
        for index in indexs:
            index_info[index.get_category_display()].append(index)
        return index_info

    @classmethod
    @web_cache(60)
    def data_report_info(cls, cc_biz_id, hostid_list=None):
        """
        获取主机的数据上报状态
        return：
            {
                u'192.4.32.27|3': False,
                 u'10.135.59.162|1': False,
                 u'134.9.0.45|3': False,
                 u'10.104.122.152|1': False,
                 u'10.104.245.119|3': True
             }
        """
        def _make_simple_sql(rt_id):
            sql = """SELECT *
    FROM {rt_id}
    WHERE dteventtime > '{time_line}'
    GROUP BY ip, cloud_id limit {SQL_MAX_LIMIT}
            """
            from utils.trt import trans_bkcloud_rt_bizid
            kwargs = {
                'rt_id': trans_bkcloud_rt_bizid("%s_%s" % (cc_biz_id, rt_id)),
                # 获取最近5分钟的性能数据记录
                'time_line': (
                    datetime.datetime.now() - datetime.timedelta(
                        minutes=5
                    )).strftime("%Y-%m-%d %H:%M:00"),
                'SQL_MAX_LIMIT': SQL_MAX_LIMIT,
            }
            sql = sql.format(**kwargs)
            return sql
        if hostid_list is None:
            # 这里获取业务下所有主机列表
            hosts = CCBiz.hosts(cc_biz_id).get("data", [])
            hostid_list = set(
                [host_key(h) for h in hosts]
            ) if type(hosts)==list else []
        else:
            if not hasattr(hostid_list, "__iter__"):
                hostid_list = {hostid_list}
        report_info = dict().fromkeys(hostid_list, False)
        if not hostid_list:
            return report_info
        # 获取各项基础性能数据是否上报
        result_table_set = set([_h.result_table_id for _h in cls.filter(
            graph_show=True)])
        for result_table_id in result_table_set:
            try:
                ret = query(_make_simple_sql(result_table_id))
            except TableNotExistException:
                continue
            points = ret["list"]
            if points:
                for point in points:
                    # 将数据平台platid为0的转换成1
                    plat_id = str(point["cloud_id"])
                    plat_id = plat_id_gse_to_cc(plat_id)
                    key = host_key(ip=point["ip"], plat_id=plat_id)
                    if key in hostid_list and key in report_info:
                        report_info[key] = True
                        hostid_list.remove(key)
            if all(report_info.values()):
                break
        return report_info

    @property
    def desc(self):
        return self.description if self.description else self.describe

    @property
    def unit_display(self):
        return self.conversion_unit if self.conversion_unit else self.unit


class BaseHostIndex(ApiModel):

    action = "monitor/basealarm_defs"
    # property
    category = "base_alarm"

    @classmethod
    def get(cls, **kwargs):
        if "id" in kwargs:
            kwargs["alarm_type"] = kwargs["id"]
            del kwargs["id"]
        if "alarm_type" in kwargs and is_base_hostindex(kwargs["alarm_type"]):
            kwargs["alarm_type"] = page_id_to_base_hostindex_id(
                kwargs["alarm_type"]
            )
        return super(BaseHostIndex, cls).get(**kwargs)

    def __unicode__(self):
        return u"%s[%s]" % self.description, self.title

    def __init__(self, kwargs=None):
        super(BaseHostIndex, self).__init__(kwargs)
        if self and not is_base_hostindex(self.id):
            self.id = base_hostindex_id_to_page_id(self.alarm_type)

    @property
    def real_id(self):
        return self.alarm_type

    @property
    def result_table_id(self):
        return u"基础"

    @property
    def item(self):
        return self.title

    @property
    def desc(self):
        return self.description

    @classmethod
    def get_base_hostindex_options(cls):
        base_hostindex = {"text": u"基础", "children": [], "category": "base"}
        base_alarms = cls.objects.filter(is_enable=True)
        children = []
        for _h in base_alarms:
            info = dict(id=base_hostindex_id_to_page_id(_h.alarm_type), item=_h.title,
                        text=_h.description, unit="")
            children.append(info)
        base_hostindex["children"] = children
        return base_hostindex


class BasePerformanceClient(object):
    # 基础性能数据获取

    client_pool = dict()

    def __new__(cls, cc_biz_id, hostindex_id_or_obj, max_minutes_delay=10):
        _instance = cls.client_pool.get(
            "%s:%s" % (
                cc_biz_id,
                getattr(hostindex_id_or_obj, "id", hostindex_id_or_obj)
            )
        )
        if _instance is not None:
            return _instance
        else:
            return super(BasePerformanceClient, cls).__new__(
                cls, cc_biz_id, hostindex_id_or_obj, max_minutes_delay
            )

    def __init__(self, cc_biz_id, hostindex_id_or_obj, max_minutes_delay=10):
        """
        :type self: object
        """
        self.cc_biz_id = cc_biz_id
        self.max_minutes_delay = max_minutes_delay
        if isinstance(hostindex_id_or_obj, HostIndex):
            self.hostindex = hostindex_id_or_obj
        else:
            self.hostindex = HostIndex.get(pk=hostindex_id_or_obj)
        self.latest_time = None
        BasePerformanceClient.client_pool[
            "%s:%s" % (cc_biz_id, self.hostindex.id)
        ] = self

    def _make_sql(self, host_id=None):
        sql = """SELECT *
FROM {rt_id}
WHERE dteventtime > '{time_line}' {host_id_filter}
ORDER BY dteventtime DESC limit {SQL_MAX_LIMIT}"""
        host_id_filter_str = ""
        if host_id is not None:
            ip, plat_id = parse_host_id(host_id)
            plat_id = plat_id_cc_to_gse(plat_id)
            host_id_filter_str = ("and ip='%s' and cloud_id='%s'" %
                                  (ip, plat_id))
        from utils.trt import trans_bkcloud_rt_bizid
        kwargs = {
            'rt_id': trans_bkcloud_rt_bizid("%s_%s" % (
                self.cc_biz_id, self.hostindex.result_table_id
            )),
            # 获取最近5分钟的性能数据记录
            'time_line': (
                datetime.datetime.now() - datetime.timedelta(
                    minutes=5
                )).strftime("%Y-%m-%d %H:%M:00"),
            'host_id_filter': host_id_filter_str,
            'SQL_MAX_LIMIT': SQL_MAX_LIMIT,
        }
        sql = sql.format(**kwargs)
        return sql

    @web_cache(60, db_cache=False)
    def _fatch_point(self, host_id=None):
        ret = query(self._make_sql(host_id=host_id))
        data_detail = ret["list"]
        return data_detail

    def performance_points(self, item_field=None, host_id=None):
        # 获取业务下所有主机最新性能信息, 支持获取单个主机新更能信息
        if item_field is None:
            item_field = self.hostindex.item
        points = self._fatch_point(host_id)
        performance_point_info = dict()
        if points:
            self.latest_time = points[0]['dtEventTime']
            for point in points:
                # 将数据平台platid为0的转换成1
                plat_id = str(point["cloud_id"])
                plat_id = plat_id_gse_to_cc(plat_id)
                key = host_key(ip=point["ip"], plat_id=plat_id)
                if self.hostindex.dimension_field:
                    dimension = point[self.hostindex.dimension_field]
                    key = "%s:%s" % (key, dimension)
                if key not in performance_point_info:
                    performance_point_info[key] = {
                        "val": point[item_field] / self.hostindex.conversion,
                        "unit": self.hostindex.unit_display
                    }
                else:
                    continue
            if self.hostindex.dimension_field:
                new_performance_point_info = dict()
                for k, v in performance_point_info.iteritems():
                    key, dimension = k.split(':')
                    bp_item = {
                        dimension: v["val"]
                    }
                    if key not in new_performance_point_info:
                        new_performance_point_info[key] = {
                            "val": [bp_item],
                            "unit": v["unit"]
                        }
                    else:
                        new_performance_point_info[key]["val"].append(bp_item)
                performance_point_info = new_performance_point_info
                for host_id, val in performance_point_info.iteritems():
                    performance_point_info[host_id]["val"] = sorted(
                        val["val"], key=lambda x: str(x.keys()[0])
                    )
        return performance_point_info


class AlarmInstance(ApiModel):
    action = "alarm/alarms"

    USER_STATUS_CHOICES = (
        ('received', u'收到'),  # 已收到告警
        ('skipped', u'被收敛'),  # 处理跳过
        ('shield', u'被屏蔽'),
        ('notified', u'已通知')
    )

    USER_STATUS_DESC_HTML = {
        "notified": u"<span class='label label-success cure-status' "
                    u"data-toggle='tooltip' data-placement='right' title=''>"
                    u"已通知</span>",
        "received": u"<span class='label label-info cure-status' "
                    u"data-toggle='tooltip' data-placement='right' title=''>"
                    u"收到</span>",
        "skipped": u"<span class='label label-default cure-status' "
                   u"data-toggle='tooltip' data-placement='right' title=''>"
                   u"已收敛</span>",
        "shield": u"<span class='label label-default cure-status' "
                  u"data-toggle='tooltip' data-placement='right' title=''>"
                  u"已屏蔽</span>"
    }

    ALARM_LEVEL = [
        ('3', u'轻微'),
        ('2', u'普通'),
        ('1', u'严重'),
    ]

    ALARM_LEVEL_COLOR = [
        ('3', 'text-muted'),
        ('2', 'text-info'),
        ('1', 'text-danger'),
    ]

    default_status_html = (u"<span class='label label-info cure-status' "
                           u"data-toggle='tooltip' data-placement='right' "
                           u"title=''>告警中</span>")

    MONITOR_TYPE_CHOICES = (
        ("base_alarm", u"基础"),
        # ("basic", u"基础"),
        ("base", u"基础"),
        ("cpu", u"CPU"),
        ("mem", u"内存"),
        ("net", u"网络"),
        ("disk", u"磁盘"),
        ("custom", u"自定义"),
    )

    @classmethod
    def get_alarm_count_by_host_id_list(cls, host_id_list, cc_biz_id, date_str):
        # 根据主机列表和日期拉取告警事件数
        try:
            start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            end = start + datetime.timedelta(seconds=3600 * 24 - 1)
        except AttributeError:
            # 多线程处理导致的 AttributeError: _strptime
            return cls.get_alarm_list_by_host_id(host_id_list, cc_biz_id, date_str)
        ip_list = list()
        if not hasattr(host_id_list, "__iter__"):
            host_id_list = host_id_list.split(',')
        for host_id in host_id_list:
            if host_id:
                ip, plat_id = parse_host_id(host_id)
                ip_list.append(ip)
        params = {
            "source_time__gte": arrow.get(start).format("YYYY-MM-DD HH:mm:SS"),
            "source_time__lte": arrow.get(end).format("YYYY-MM-DD HH:mm:SS"),
            "cc_biz_id": cc_biz_id,
            "ip__in": ','.join(ip_list),
            "group_field": 'ip,cc_plat_id',
        }
        res = requests_get(cls.get_url()+"dimension_cnts/", **params)
        if res.get("result"):
            return res["data"]
        return {}

    @classmethod
    def get_alarm_list_by_host_id(cls, host_id, cc_biz_id, date_str):
        # 根据主机信息和日期拉取告警事件列表
        try:
            start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            end = start + datetime.timedelta(seconds=3600 * 24 - 1)
        except AttributeError:
            # 多线程处理导致的 AttributeError: _strptime
            return cls.get_alarm_list_by_host_id(host_id, cc_biz_id, date_str)
        ip, plat_id = parse_host_id(host_id)
        params = {
            "source_time__gte": arrow.get(start).format("YYYY-MM-DD HH:mm:SS"),
            "source_time__lte": arrow.get(end).format("YYYY-MM-DD HH:mm:SS"),
            "cc_biz_id": cc_biz_id,
            "ip": ip,
            "cc_plat_id": plat_id,
            "ordering": "-source_time"
        }
        alarms = cls.objects.filter(**params)
        return alarms

    @classmethod
    def get_alarm_list_by_strategy_id(cls, alarm_strategy, date_str,
                                      cc_biz_id):
        # 根据策略id和日期拉取告警事件列表
        try:
            start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            end = start + datetime.timedelta(seconds=3600 * 24 - 1)
        except AttributeError:
            # 多线程处理导致的 AttributeError: _strptime
            return cls.get_alarm_list_by_strategy_id(
                alarm_strategy, date_str, cc_biz_id
            )
        try:
            if not check_permission(alarm_strategy, cc_biz_id):
                return []
            alarm_def_id = alarm_strategy.alarm_def_id
            alarm_def = AlarmDef.objects.get(id=alarm_def_id)
        except JAItemDoseNotExists:
            return []
        kwargs = {
            "source_time__gte": arrow.get(start).format("YYYY-MM-DD HH:mm:SS"),
            "source_time__lte": arrow.get(end).format("YYYY-MM-DD HH:mm:SS"),
            "alarm_source_id": alarm_def.id,
            "cc_biz_id": cc_biz_id,
            "ordering": "-source_time"
        }
        alarms = cls.objects.filter(**kwargs)
        return alarms

    @classmethod
    def get_alarm_by_monitor_id(cls, start, end, monitor_id):
        """根据monitor id获取告警,包含已删除/禁用的策略产生的告警"""
        alarm_sources = AlarmDef.objects.filter(alarm_attr_id=str(monitor_id))
        alarm_source_ids = [str(alarm_source.id)
                            for alarm_source in alarm_sources]
        if not alarm_source_ids:
            return []
        kwargs = {
            "source_time__gte": arrow.get(start).format("YYYY-MM-DD HH:mm:SS"),
            "source_time__lte": arrow.get(end).format("YYYY-MM-DD HH:mm:SS"),
            "alarm_source_id__in": ",".join(alarm_source_ids),
            "user_status__in": ",".join([u"received", u"notified"]),
            "ordering": "-source_time"
        }
        alarms = cls.objects.filter(**kwargs)
        return alarms

    @property
    def detail(self):
        _content = json.loads(self.alarm_content) if self.alarm_content else {}
        content = _content.get("content", u"无")
        dimension = _content.get("dimension", u"无")
        source_name = _content.get("source_name", u"无")
        alarm_info = {
            "source_time": self.source_time,
            "monitor_field_show_name": source_name,
            "level_class": self.get_level_color(),
            "level_display": self.get_level_display(),
            "dimensions_display": dimension,
            "level": self.level,
            "raw": content,
            "status_html": self.status_html
        }
        return alarm_info

    @property
    def origin_alarm__snapshot(self):
        """
        获取原始告警快照
        """
        return json.loads(self.origin_alarm or "{}")

    def get_level_display(self):
        level_dict = dict(self.ALARM_LEVEL)
        return level_dict.get(str(self.level), level_dict["1"])

    def get_level_color(self):
        color_dict = dict(self.ALARM_LEVEL_COLOR)
        return color_dict.get(str(self.level), color_dict["1"])

    def get_alarm_type_display(self):
        alarm_type_desc = dict(self.MONITOR_TYPE_CHOICES).get(
            self.alarm_type, self.alarm_type)
        if self.source_type == "ALERT":
            return dict(Monitor.MONITOR_TYPE_CHOICES).get(
                self.origin_alarm__snapshot["monitor_type"],
                self.origin_alarm__snapshot["monitor_type"])
        return alarm_type_desc

    def get_dimensions_display(self):
        _content = json.loads(self.alarm_content) if self.alarm_content else {}
        return _content.get("dimension")

    def get_raw_display(self):
        _content = json.loads(self.alarm_content) if self.alarm_content else {}
        content = _content.get("content")
        if content:
            return content
        return self.raw


    @property
    def status_html(self):
        return self.USER_STATUS_DESC_HTML.get(
            self.user_status, self.user_status
        )

    @property
    def extend_message(self):
        try:
            origin_alarm = json.loads(self.origin_alarm)
            return origin_alarm.get("extend_message") or ""
        except ValueError:
            return ""

    @property
    def dimensions(self):
        """
        获取匹配维度
        """
        try:
            dimensions = json.loads(self.match_dimension)
        except ValueError:
            dimensions = {}
        dimensions.pop("anomaly_type", None)
        dimensions.pop("biz_id", None)
        if not dimensions and self.ip:
            dimensions["ip"] = self.ip
        return dimensions

    @property
    def monitor(self):
        snapshot = json.loads(self.snap_alarm_source or "{}")
        try:
            return Monitor.objects.get(id=snapshot["alarm_attr_id"])
        except JAItemDoseNotExists:
            return None


class Monitor(ApiModel):
    action = "monitor/monitors"
    SCENARIO_CHOICES = (
        ("performance", u"主机性能"),
        ("custom", u"自定义"),
        ("base_alarm", u"基础"),
    )

    MONITOR_TYPE_CHOICES = (
        ("cpu", u"CPU"),
        ("mem", u"内存"),
        ("net", u"网络"),
        ("disk", u"磁盘"),
        ("base_alarm", u"基础"),
        ("custom", u"自定义"),
    )

    def get_scenario_display(self):
        return dict(Monitor.SCENARIO_CHOICES).get(
            self.scenario, self.scenario
        )

    def get_monitor_type_display(self):
        return dict(Monitor.MONITOR_TYPE_CHOICES).get(
            self.monitor_type, self.monitor_type
        )

    def __init__(self, kwargs=None):
        try:
            if type(kwargs) is not dict:
                kwargs = dict()
            stat_source_info = kwargs.get('stat_source_info', '')
            stat_source_info = json.loads(stat_source_info)
        except Exception, e:
            stat_source_info = {}
        try:
            kwargs['generate_config_id'] = stat_source_info.get(
                'generate_config_id', 0
            )
        except Exception, e:
            kwargs['generate_config_id'] = 0
        super(Monitor, self).__init__(kwargs)

    @classmethod
    def filter(cls, **kwargs):
        monitor_list = super(Monitor, cls).filter(**kwargs)
        new = list()
        key_list = [
            "count_freq",
            "aggregator",
            "monitor_field",
            "monitor_result_table_id"
            ]
        for m in monitor_list:
            for k in key_list:
                if k in kwargs and str(getattr(m, k)) != str(kwargs[k]):
                    break
            else:
                new.append(m)
        return new

    @classmethod
    def create(cls, biz_id, scenario, monitor_type, monitor_name, monitor_desc,
               monitor_target, monitor_result_table_id, monitor_field,
               generate_config_id=0, access_params=False):
        monitor_type = monitor_type.lower()
        kwargs = {
            'biz_id': biz_id,
            'title': monitor_name,
            'description': monitor_desc,
            'monitor_target': monitor_target,
            'scenario': scenario,
            'stat_source_type': 'BKDATA' if scenario != 'base_alarm' else '',
            'stat_source_info': json.dumps({
                "monitor_result_table_id": monitor_result_table_id,
                "monitor_field": monitor_field
            }),
            'src_type': 'GSE' if scenario == 'base_alarm' else 'JA',
            'monitor_type': monitor_type,
            'generate_config_id': generate_config_id,
            'is_enabled': True,
            'is_deleted': False
        }
        if access_params:
            kwargs['access_params'] = json.dumps(access_params)

        res = requests_post(cls.get_url(), **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=cls.get_url(), method="POST",
            param=json.dumps(kwargs), result=res)
        obj = cls(cls.parse_api_response(res))
        from monitor.operation_records import pre_save_models, post_save_models
        pre_save_models(sender=cls, instance=None)
        post_save_models(sender=cls, instance=obj, created=True)
        return obj

    @classmethod
    def get_active_performance_monitors(cls, cc_biz_id):
        monitors = cls.objects.filter(
            biz_id=cc_biz_id,
            is_deleted=False,
            scenario__in="performance,base_alarm"
        )
        return monitors

    @property
    def condition_list(self):
        @lazy_property()
        def _condition_list(self):
            return MonitorCondition.objects.filter(monitor_id=self.id)
        return _condition_list(self)

    @property
    def monitor_name(self):
        return self.title

    @property
    def monitor_field_show_name(self):
        """监控指标，页面输出
        TODO
        """
        if self.scenario in ["performance", "base_alarm"]:
            return self.monitor_name
        return self.monitor_field

    @property
    def monitor_result_table_id(self):
        @lazy_property()
        def _monitor_result_table_id(self):
            return json.loads(self.stat_source_info).get(
                "monitor_result_table_id"
            ) or ""
        return _monitor_result_table_id(self)

    @property
    def monitor_field(self):
        @lazy_property()
        def _monitor_field(self):
            return json.loads(self.stat_source_info).get("monitor_field") or ""
        return _monitor_field(self)

    @property
    def backend_id(self):
        return self.id

    @property
    def monitor_desc(self):
        return self.description

    @property
    def count_method(self):
        _count_method = json.loads(self.stat_source_info).get(
            "aggregator"
        ) or ""
        if not _count_method:
            from monitor.models import DataResultTableField
            try:
                _count_method = DataResultTableField.objects.get(
                    result_table_id=self.monitor_result_table_id,
                    generate_config_id=self.generate_config_id,
                    field=self.monitor_field).processor
            except DataResultTableField.DoesNotExist:
                _count_method = "sum"
        if _count_method == "projector":
            _count_method = "avg"
        return _count_method

    @property
    def dimensions(self):
        from monitor.models import DataResultTableField
        result_table_field = DataResultTableField.objects.filter(
            result_table_id=self.monitor_result_table_id,
            generate_config_id=self.generate_config_id
        )
        if not result_table_field:
            from utils.trt import list_result_table_detail
            result_table_field = []
            table_list = list_result_table_detail(
                biz_id=self.biz_id)['data']
            rt_info = filter(lambda r: r["id"] == self.monitor_result_table_id, table_list)
            if rt_info:
                rt_info = rt_info[0]
                for index, field in enumerate(rt_info['fields']):
                    is_dimension = field.get('is_dimension', False)
                    rt_field_obj = DataResultTableField(
                        monitor_id=self.id,
                        result_table_id=rt_info['id'],
                        field=field['field'],
                        desc=field.get("description", ""),
                        field_type=field['type'],
                        processor=field.get('processor'),
                        processor_args=field.get('processor_args'),
                        is_dimension=is_dimension,
                        origins=json.dumps(field.get('origins', '')),
                        generate_config_id=self.generate_config_id,
                        field_index=index)
                    rt_field_obj.save()
                    result_table_field.append(rt_field_obj)
        return filter(lambda x: x.is_dimension, result_table_field)

    @property
    def favorite(self):
        # 收藏状态
        from monitor.models import ScenarioMenu, MonitorLocation
        try:
            sm = ScenarioMenu.objects.get(system_menu=u"favorite",
                                          biz_id=self.biz_id)
            return MonitorLocation.objects.filter(
                monitor_id=self.id, menu_id=sm.id,
                biz_id=self.biz_id).exists()
        except ScenarioMenu.DoesNotExist:
            return False

    @property
    def result_table(self):
        from monitor.models import DataResultTable
        try:
            return DataResultTable.objects.get(
                result_table_id=self.monitor_result_table_id,
                generate_config_id=self.generate_config_id)
        except DataResultTable.DoesNotExist, e:
            return DataResultTable(count_freq=60)

    @property
    def monitor_source(self):
        from monitor.models import DataGenerateConfig, DataCollector
        try:
            generate_config = DataGenerateConfig.objects.get(
                id=self.generate_config_id)
            collector = DataCollector.objects.get(
                id=generate_config.collector_id)
            return dict(
                id=collector.data_id,
                text=u"【%s】%s" % (collector.data_id, collector.data_set))
        except:
            return dict(
                id=self.monitor_result_table_id,
                text=self.monitor_result_table_id)

    def get_title(self):
        return u'监控(%s)' % self.monitor_name

    def get_operate_changed_config(self, ori_data):
        changed_configs = {}
        if self.monitor_name != ori_data.monitor_name:
            changed_configs['monitor_name'] = {
                'key': 'monitor_name',
                'title': u'监控名称',
                'ori_value': ori_data.monitor_name,
                'dst_value': self.monitor_name
            }
        if self.monitor_desc != ori_data.monitor_desc:
            changed_configs['monitor_desc'] = {
                'key': 'monitor_desc',
                'title': u'备注',
                'ori_value': ori_data.monitor_desc,
                'dst_value': self.monitor_desc
            }
        if self.monitor_field != ori_data.monitor_field:
            changed_configs['monitor_field'] = {
                'key': 'monitor_field',
                'title': u'监控字段',
                'ori_value': ori_data.monitor_field,
                'dst_value': self.monitor_field
            }
        if self.is_enabled != ori_data.is_enabled:
            changed_configs['is_enabled'] = {
                'key': 'is_enabled',
                'title': u'状态',
                'ori_value': u'已启用' if ori_data.is_enabled else u'未启用',
                'dst_value': u'已启用' if self.is_enabled else u'未启用'
            }
        return changed_configs

    def gen_op_desc_by_changed_config(self, changed):
        op_desc = ''
        if len(changed) < 1:
            return op_desc
        for key in changed:
            changed_attr = changed[key]
            op_desc += u"监控配置的%s由 %s 被修改为 %s\n" % (
                changed_attr.get('title', key),
                changed_attr.get('ori_value', ''),
                changed_attr.get('dst_value', ''))
        return op_desc

class MonitorCondition(ApiModel):
    action = "monitor/monitor_items"

    @classmethod
    def create(cls, alarmstrategy, monitor):
        kwargs = alarmstrategy.gen_monitor_items_config(monitor)
        res = requests_post(cls.get_url(), **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=cls.get_url(), method="POST",
            param=json.dumps(kwargs), result=res)
        obj = cls(cls.parse_api_response(res))
        from monitor.operation_records import pre_save_models, post_save_models
        pre_save_models(sender=cls, instance=None)
        post_save_models(sender=cls, instance=obj, created=True)
        return obj

    @property
    def condition_config(self):
        @lazy_property()
        def _condition_config(self):
            return MonitorConditionConfig.objects.get(monitor_item_id=self.id)
        return _condition_config(self)

    @condition_config.setter
    def condition_config(self, val):
        cache_key = lazy_property.gen_cache_key(self, "_condition_config")
        # 设置缓存
        setattr(self, cache_key, val)

    @property
    def alarm_def(self):
        @lazy_property()
        def _alarm_def(self):
            return AlarmDef.objects.get(id=self.alarm_def_id)
        return _alarm_def(self)

    @alarm_def.setter
    def alarm_def(self, val):
        cache_key = lazy_property.gen_cache_key(self, "_alarm_def")
        # 设置缓存
        setattr(self, cache_key, val)

    @property
    def condition_dict(self):
        _condition_dict = dict()
        condition = json.loads(self.condition or "[[]]")[0]
        for c in condition:
            val = c["value"]
            if isinstance(val, list):
                val = ",".join(map(str, val))
            _condition_dict[c["field"]] = val
        return _condition_dict


class MonitorConditionConfig(ApiModel):
    action = "monitor/detect_algorithm_configs"

    @classmethod
    def create(cls, alarmstrategy, monitor_item):
        kwargs = alarmstrategy.gen_detect_algorithm_config(monitor_item)
        res = requests_post(cls.get_url(), **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=cls.get_url(), method="POST",
            param=json.dumps(kwargs), result=res)
        obj = cls(cls.parse_api_response(res))
        from monitor.operation_records import pre_save_models, post_save_models
        pre_save_models(sender=cls, instance=None)
        post_save_models(sender=cls, instance=obj, created=True)
        return obj

    @property
    def strategy_option(self):
        return self.config

    def get_title(self):
        try:
            condition = MonitorCondition.objects.get(id=self.monitor_item_id)
            alarm_def = AlarmDef.objects.filter(id=condition.alarm_def_id)[0]
        except Exception, e:
            return u'检测算法'
        return u'告警策略(%s)的检测算法' % alarm_def.title

    def get_operate_changed_config(self, ori_data):
        changed_configs = {}
        from monitor.models import AlarmStrategy
        if self.strategy_option != ori_data.strategy_option:
            changed_configs['strategy_option'] = {
                'key': 'strategy_option',
                'title': u'检测算法',
                'ori_value': "%s %s" % (
                    AlarmStrategy.gen_strategy_name(ori_data.algorithm_id),
                    AlarmStrategy.gen_strategy_desc(
                        ori_data.algorithm_id, ori_data.config)
                ),
                'dst_value': "%s %s" % (
                    AlarmStrategy.gen_strategy_name(self.algorithm_id),
                    AlarmStrategy.gen_strategy_desc(
                        self.algorithm_id, self.config)
                )
            }
        return changed_configs

    def gen_op_desc_by_changed_config(self, changed):
        op_desc = ''
        if len(changed) < 1:
            return op_desc

        for key in changed:
            changed_attr = changed[key]
            op_desc += u"告警策略的%s由 %s 被修改为 %s\n" % (
                changed_attr.get('title', key),
                changed_attr.get('ori_value', ''),
                changed_attr.get('dst_value', ''))
        return op_desc


class AlarmDef(ApiModel):
    action = "alarm/alarm_sources"

    # 超时时长 default: 40
    timeout = 40

    @classmethod
    def create(cls, alarmstrategy, monitor):
        kwargs = alarmstrategy.gen_alarm_sources_config(monitor)
        res = requests_post(cls.get_url(), **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=cls.get_url(), method="POST",
            param=json.dumps(kwargs), result=res)
        obj = cls(cls.parse_api_response(res))
        from monitor.operation_records import (pre_save_models,
                                               post_save_models)
        pre_save_models(sender=cls, instance=None)
        post_save_models(sender=cls, instance=obj, created=True)
        return obj

    def update(self, **kwargs):
        cls = self.__class__
        url = cls.get_url(pk=self.id)
        from monitor.operation_records import (pre_save_models,
                                               post_save_models)
        pre_save_models(sender=cls, instance=self)

        # 删除掉alarm_converge
        if 'alarm_converge_config' in kwargs:
            converges = AlarmConvergeConfig.objects.filter(
                alarm_source_id=self.id
            )
            for converge in converges:
                converge.delete()

        res = requests_post(url, **kwargs)
        post_save_models(sender=cls,
                         instance=cls(cls.parse_api_response(res)),
                         created=False)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=url, method="POST",
            param=json.dumps(kwargs), result=res)
        return cls(cls.parse_api_response(res))

    @property
    def converge(self):
        @lazy_property()
        def _converge(self):
            return AlarmConvergeConfig.objects.get(
                alarm_source_id=self.id
            ).config
        try:
            return _converge(self)
        except JAItemDoseNotExists:
            return '{}'

    @converge.setter
    def converge(self, val):
        cache_key = lazy_property.gen_cache_key(self, "_converge")
        # 设置缓存
        setattr(self, cache_key, val)

    @property
    def notify(self):
        return self.alarm_notice_config.notify_config

    @property
    def notify_dict(self):
        _notify_dict = json.loads(self.notify or "{}")
        # alarm_start_time, alarm_end_time 实际生效的是alarm_notice_config的属性
        return _notify_dict

    @property
    # alarm_def.condition - > alarm_def.monitor_item
    def monitor_item(self):
        @lazy_property()
        def _monitor_item(self):
            return MonitorCondition.objects.get(alarm_def_id=self.id)
        return _monitor_item(self)

    @property
    def alarm_notice_config(self):
        @lazy_property()
        def _alarm_notice_config(self):
            return AlarmNoticeConfig.objects.get(id=self.alarm_notice_id)
        return _alarm_notice_config(self)

    @alarm_notice_config.setter
    def alarm_notice_config(self, val):
        cache_key = lazy_property.gen_cache_key(self, "_alarm_notice_config")
        # 设置缓存
        setattr(self, cache_key, val)

    @classmethod
    def get_alarmdef_info_by_monitor(cls, monitor):
        def alarmdef_to_dict(obj):
            return {"id": obj.id, "text": obj.description}
        alarm_def_list = list()
        set_rel(monitor.condition_list, AlarmDef, "alarm_def", "alarm_def_id", "id")
        for condition in monitor.condition_list:
            alarm_def_list.append(condition.alarm_def)
        return map(alarmdef_to_dict, alarm_def_list)

    def get_title(self):
        return u'告警策略(%s)' % self.title

    def get_operate_changed_config(self, ori_data):
        changed_configs = {}

        if self.is_enabled != ori_data.is_enabled:
            changed_configs['is_enabled'] = {
                'key': 'is_enabled',
                'title': u'状态',
                'ori_value': u'已启用' if ori_data.is_enabled else u'未启用',
                'dst_value': u'已启用' if self.is_enabled else u'未启用'
            }

        if self.condition != ori_data.condition:
            try:
                ori_condition = json.loads(ori_data.condition)
                ori_condition_dict = {}
                for cond in ori_condition[0]:
                    ori_condition_dict[cond['field']] = cond['value']
            except Exception, e:
                ori_condition_dict = {}
            try:
                condition = json.loads(self.condition)
                condition_dict = {}
                for cond in condition[0]:
                    condition_dict[cond['field']] = cond['value']
            except Exception, e:
                condition_dict = {}

            ori_prform_cate = ('ip' if 'ip' in ori_condition_dict.keys()
                               else 'set')
            prform_cate = 'ip' if 'ip' in condition_dict.keys() else 'set'
            # 如果是base_alarm,
            ori_type = ('performance'
                        if ori_data.scenario in ['base_alarm', 'performance']
                        else ori_data.scenario)
            dst_type = ('performance'
                        if self.scenario in ['base_alarm', 'performance']
                        else self.scenario)
            if ori_type == 'performance':
                ori_condition_obj = ori_condition_dict
            else:
                ori_condition_obj = ori_data.condition

            if dst_type == 'performance':
                condition_obj = condition_dict
            else:
                condition_obj = self.condition

            from monitor.models import AlarmStrategy
            changed_configs['condition'] = {
                'key': 'condition',
                'title': u'监控对象',
                'ori_value': AlarmStrategy.gen_condition_str(
                    ori_condition_obj,
                    scenario=ori_type,
                    cc_biz_id=ori_data.biz_id,
                    cc_module=ori_condition_dict.get('cc_module', ''),
                    cc_set=ori_condition_dict.get('cc_set', ''),
                    prform_cate=ori_prform_cate,
                    ip=ori_condition_dict.get('ip', '')
                ),
                'dst_value': AlarmStrategy.gen_condition_str(
                    condition_obj,
                    scenario=dst_type,
                    cc_biz_id=self.biz_id,
                    cc_module=condition_dict.get('cc_module', ''),
                    cc_set=condition_dict.get('cc_set', ''),
                    prform_cate=prform_cate,
                    ip=condition_dict.get('ip', '')
                )
            }
        if self.description != ori_data.description:
            changed_configs['description'] = {
                'key': 'description',
                'title': u'备注',
                'ori_value': ori_data.description,
                'dst_value': self.description
            }
        from monitor.models import AlarmStrategy
        if (ori_data.converge_string !=
                AlarmStrategy.gen_converge_str(self.converge)):
            changed_configs['converge'] = {
                'key': 'converge',
                'title': u'收敛规则',
                'ori_value': ori_data.converge_string,
                'dst_value': AlarmStrategy.gen_converge_str(self.converge)
            }

        notify_way = []
        try:
            notify = json.loads(self.notify)
            for key in notify:
                if 'notify_' in key:
                    notify_way.append(key.replace('notify_', ''))
        except Exception, e:
            notify = {}
        notify_string = AlarmStrategy.gen_notify_final_str(notify_way, notify)
        if ori_data.notify_string != notify_string:
            changed_configs['notify'] = {
                'key': 'notify',
                'title': u'通知配置',
                'ori_value': ori_data.notify_string,
                'dst_value': notify_string
            }
        if self.solution_id != ori_data.solution_id:
            changed_configs['solution_id'] = {
                'key': 'solution_id',
                'title': u'处理方式',
                'ori_value': ori_data.solution_id,
                'dst_value': self.solution_id
            }
        return changed_configs

    def gen_op_desc_by_changed_config(self, changed):
        op_desc = ''
        if len(changed) < 1:
            return op_desc

        for key in changed:
            changed_attr = changed[key]
            op_desc += u"告警策略的%s由 %s 被修改为 %s\n" % (
                changed_attr.get('title', key),
                changed_attr.get('ori_value', ''),
                changed_attr.get('dst_value', ''))
        return op_desc


class AlarmConvergeConfig(ApiModel):
    action = "alarm/converge_configs"


class AlarmNoticeConfig(ApiModel):
    action = "alarm/notice_configs"


class ShieldApi(ApiModel):
    action = "alarm/shield_configs"

    @staticmethod
    def save_shield(shield):
        kwargs = ShieldApi.gen_shield_param(shield)
        url = ShieldApi.get_url(pk=shield.backend_id)
        res = requests_post(url, **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=ShieldApi.action, url=url, method="POST",
            param=json.dumps(kwargs), result=res)
        return res

    @staticmethod
    def gen_shield_param(shield):
        try:
            biz_ids = json.loads(shield.biz_id)
            biz_id = biz_ids[0]
        except Exception, e:
            biz_id = 0

        # 过滤掉ID为0的
        try:
            dimensions = json.loads(shield.dimension)
        except Exception, e:
            dimensions = {}
        for key in dimensions.keys():
            value = dimensions[key]
            if (type(value) is list) and len(value) == 1:
                if "%s" % value[0] == "0":
                    del dimensions[key]
        dimensions = json.dumps(dimensions)

        result = {
            'biz_id': biz_id,
            # 'description': shield.description,
            'begin_time': str(shield.begin_time),
            'end_time': str(shield.end_time),
            'dimensions': dimensions,
            'is_deleted': shield.is_deleted
        }
        return result


class NoticeGroups(ApiModel):
    action = "alarm/notice_groups"

    @classmethod
    def create(cls, biz_id, title, description, group_receiver, group_type=0,):
        kwargs = {
            'biz_id': biz_id,
            'title': title,
            'description': description,
            'group_receiver': group_receiver,
            'group_type': group_type,
            'is_enabled': True,
            'is_deleted': False
        }
        res = requests_post(cls.get_url(), **kwargs)
        from monitor.models import CallMethodRecord
        CallMethodRecord.objects.create(
            action=cls.action, url=cls.get_url(), method="POST",
            param=json.dumps(kwargs), result=res)
        obj = cls(cls.parse_api_response(res))
        from monitor.operation_records import pre_save_models, post_save_models
        pre_save_models(sender=cls, instance=None)
        post_save_models(sender=cls, instance=obj, created=True)
        return obj

    def group_uer_display(self):
        user_info = get_nick_by_uin(self.group_receiver, show_detail=True)
        return ';'.join(user_info.values())

    def alarm_def_list(self):
        # 获取配置了该通知组的所有策略
        url = "%snotice_group/%s/" % (AlarmDef.get_url(), self.id)
        res = requests_get(url)
        item_list = AlarmDef.parse_api_response(res)
        return [AlarmDef(item) for item in item_list]


def set_rel(obj_list, rel_model, property_name, foreignkey, to_field, val_func=None):
    """
    基于api model 实现Foreign key的功能
    :param obj_list: 对象列表
    :param rel_model: 关联对象类，也可以是以实例化的关联对象列表
    :param property_name: 对象属性
    :param foreignkey: 对象外键字段
    :param to_field: 外键对应关联对象的字段
    :param val_func: 对象属性值处理函数，默认不再处理
    :return:
    """
    if not hasattr(rel_model, "__iter__"):
        rel_obj_id_range_str = ",".join(map(str, [getattr(obj, foreignkey) for obj in obj_list]))
        kwargs = {
            "%s__in" % to_field: rel_obj_id_range_str
        }
        rel_obj_list = rel_model.objects.filter(**kwargs)
    else:
        rel_obj_list = rel_model
    if not (val_func and callable(val_func)):
        val_func = lambda x: x
    rel_obj_maping = {getattr(r_obj, to_field): r_obj for r_obj in rel_obj_list}
    for obj in obj_list:
        val = val_func(rel_obj_maping.get(getattr(obj, foreignkey), None))
        setattr(obj, property_name, val)
    return obj_list