# -*- coding: utf-8 -*-
import datetime
import json
import time
import urllib
import arrow

import requests
from django.conf import settings

from common.log import logger
from monitor.constants import CONDITION_CONFIG, HOST_POINT_INTERVAL, \
    POINT_DELAY_SECONDS, POINT_DELAY_COLOR, DATA_API, SQL_MAX_LIMIT
from monitor.errors import (EmptyQueryException, TableNotExistException,
                            SqlQueryException)
from utils.cache import web_cache
from utils.common_utils import today_start_timestamp
from utils.requests_utils import INTERFACE_COMMON_PARAMS, get_bk_token

TIME_OFFSET = 8 * 3600 * 1000


class DataProcessor(object):
    @staticmethod
    def get_splw_time_range(date_obj_range):
        # 根据时间范围计算出同比的时间范围
        start, end = date_obj_range
        # 上周同比
        return start - datetime.timedelta(7), end - datetime.timedelta(7)

    @staticmethod
    def get_lp_time_range(date_obj_range):
        # 根据时间范围计算出环比的时间范围
        start, end = date_obj_range
        date_difference = (end - start).days
        if date_difference == 0:
            date_difference += 1
        return (start - datetime.timedelta(date_difference),
                end - datetime.timedelta(date_difference))

    @staticmethod
    def make_time_range_filter_dict(date_obj_range, time_field,
                                    filter_dict=None):
        # 根据时间范围，更新过滤字典
        if filter_dict is None:
            filter_dict = dict()
        time_range = (
            date_obj_range[0].strftime("%Y%m%d"),
            (date_obj_range[1] + datetime.timedelta(1)).strftime("%Y%m%d")
        )
        filter_dict['thedate__gte'], filter_dict['thedate__lt'] = time_range
        filter_dict['dteventtime__gte'], filter_dict['dteventtime__lte'] = map(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S"), date_obj_range
        )
        return filter_dict


    @staticmethod
    def operation_monitor_data(result_table_id, value_field, params=None,
                               group_by_field_ext='dteventtime', monitor_id=0):
        """
        获取运营图表数据 (简单版sql查询，不依赖graph表配置)
        :param result_table_id:  表id
        :param method: 度量字段统计方法
        :param params: 过滤参数
        :return:
        """

        def thedate_first(a, b):
            a = str(a)
            a_value = 0
            b = str(b)
            b_value = 0
            if a.startswith("thedate"):
                a_value += 10
            if b.startswith("thedate"):
                b_value += 10
            return cmp(a_value, b_value)

        value_field_parse_list = value_field.split(" as ")
        if len(value_field_parse_list) > 1:
            value_field_alis = value_field_parse_list[1]
        else:
            value_field = "%s as count" % value_field
            value_field_alis = "count"

        def _get_hermes_data(date_desc=u"今日", compute_delay=False):
            where_str = " where "
            where_list = DataProcessor.make_where_list(filter_dict)
            where_list = sorted(
                where_list, cmp=thedate_first, key=None, reverse=True
            )
            where_str += u" and ".join(where_list)
            select_fields_str = ",".join(
                [value_field, group_by_field_ext, "max(_ab_delay_) as delay"]
            )
            sql = (u"select %s from %s %s group by %s order by %s limit 0, %s"
                   % (select_fields_str, result_table_id, where_str,
                      group_by_field_ext, group_by_field_ext, SQL_MAX_LIMIT))
            # cache.set(cache_key, sql, 3600)
            ret = query(sql)
            data_detail = ret["list"]
            # process data
            x_axis_list = list()
            value_list = list()
            series = date_desc
            delay_info_dict = {
                series: {}
            }
            delaying = False
            zones = list()
            delay_start_point = None
            for item in data_detail:
                x_axis = str(item.get(group_by_field_ext, u" "))
                x_axis = urllib.unquote(x_axis)
                x_axis_timestamp = long(time.mktime(
                    datetime.datetime.strptime(
                        x_axis, "%Y-%m-%d %H:%M:%S"
                    ).timetuple())) + TIME_OFFSET / 1000
                delay_info_dict[series].setdefault(
                    x_axis_timestamp,
                    # 1483097260>x_axis_timestamp > 1483056000
                    item.get("delay") > POINT_DELAY_SECONDS
                )
                if compute_delay:
                    if not delaying:
                        if delay_info_dict[series].get(x_axis_timestamp, False):
                            delaying = True
                            delay_start_point = x_axis_timestamp
                    if delaying:
                        if not delay_info_dict[series].get(x_axis_timestamp, False):
                            delaying = False
                            zones.append([delay_start_point, x_axis_timestamp])

                x_axis_list.append(x_axis)
                value_count = item.get(value_field_alis)
                value_count = (round(float(value_count), 2)
                               if value_count and value_count != "null"
                               else 0)
                if value_count < 0.05:
                    value_count = (round(float(value_count), 5)
                                   if value_count and value_count != "null"
                                   else 0)
                value_list.append(value_count)
            _max_y = (max(value_list)
                      if value_list and max(value_list) > 0 else 0)
            _series_info = {"name": series,
                            "data": value_list,
                            "x_axis_list": x_axis_list,
                            "type": 'spline',
                            "percent": [],
                            "max_y": _max_y,
                            # "sql": sql,
                            "zIndex": 1}
            _series_info['count'] = _series_info['data']
            if compute_delay and zones:
                _series_info["zoneAxis"] = "x"
                _series_info["zones"] = SeriesHandleManage.make_zones_option(
                    zones
                )
                _series_info["delay_info"] = delay_info_dict[series]
            return _series_info

        if params is None:
            params = dict()
        date_obj_range = get_date_range(
            params.pop("time_range"), days=1, offset=0
        )
        filter_dict = DataProcessor.make_time_range_filter_dict(
            date_obj_range, group_by_field_ext
        )
        series_list = list()
        for k, v in params.items():
            filter_dict[k] = v
        series_info = _get_hermes_data(u"今日", compute_delay=True)
        max_y = series_info["max_y"]
        series_list.append(series_info)
        # sql = series_info["sql"]
        # 今日数据置顶
        series_info["zIndex"] = 5
        # 环比
        lp_time_range = DataProcessor.get_lp_time_range(date_obj_range)
        filter_dict = DataProcessor.make_time_range_filter_dict(
            lp_time_range, group_by_field_ext, filter_dict
        )
        series_info = _get_hermes_data(u"昨日")
        max_y = series_info["max_y"] if series_info["max_y"] > max_y else max_y
        start, end = date_obj_range
        date_difference = (end - start).days
        if date_difference == 0:
            date_difference += 1
        lp_x_axis_list = map(
            lambda x: datetime.datetime.fromtimestamp(
                long(time.mktime(datetime.datetime.strptime(
                    x, "%Y-%m-%d %H:%M:%S"
                ).timetuple()) + 3600 * 24 * date_difference)
            ).strftime("%Y-%m-%d %H:%M:%S"), series_info["x_axis_list"])
        series_info["x_axis_list"] = lp_x_axis_list
        series_list.append(series_info)
        # 同比
        splw_time_range = DataProcessor.get_splw_time_range(date_obj_range)
        filter_dict = DataProcessor.make_time_range_filter_dict(
            splw_time_range, group_by_field_ext, filter_dict
        )
        series_info = _get_hermes_data(u"上周")
        max_y = series_info["max_y"] if series_info["max_y"] > max_y else max_y
        splw_x_axis_list = map(
            lambda x: datetime.datetime.fromtimestamp(
                long(time.mktime(datetime.datetime.strptime(
                    x, "%Y-%m-%d %H:%M:%S"
                ).timetuple()) + 3600 * 24 * 7)
            ).strftime("%Y-%m-%d %H:%M:%S"), series_info["x_axis_list"])
        series_info["x_axis_list"] = splw_x_axis_list
        series_list.append(series_info)
        # process data end
        data = {
            "max_y": max_y,
            "chart_type": 'spline',
            "x_axis": {'type': 'datetime', 'minRange': 3600 * 1000},
            "series": series_list,
            "show_percent": False,
            "color_list": "",
        }
        # 实时数据
        real_time = False
        # 时间轴
        data["pointInterval"] = 5 * 1000 * 60
        data["pointStart"] = today_start_timestamp(date_obj_range[0])
        try:
            from monitor.performance.models import Monitor
            monitor = Monitor.objects.get(id=monitor_id)
            step = get_time_step(
                result_table_id, monitor.generate_config_id
            ) * 1000
        except:
            step = get_time_step(result_table_id, False) * 1000

        data["series"] = SeriesHandleManage.make_full_datetime_series(
            series_list,
            date_obj_range[0],
            date_obj_range[1],
            step,
            _format="%Y-%m-%d %H:%M:%S",
            real_time=real_time
        )
        data["series_name_list"] = [s['name'] for s in series_list]
        data["echo_sql"] = ""
        data["yaxis_range"] = 0
        return data

    @staticmethod
    def base_performance_data(result_table_id, value_field, params=None,
                              group_by_field_ext='dteventtime',group_field="",
                              cmp_date="", unit="", conversion=1,
                              series_label_show=""):
        """
        获取基础性能图表数据 (简单版sql查询，不依赖graph表配置)
        :param result_table_id:  表id
        :param params: 过滤参数
        :return:
        """
        value_field_str = "avg(%s) as %s" % (value_field.lower(),
                                             value_field.lower())

        def thedate_first(a, b):
            a = str(a)
            a_value = 0
            b = str(b)
            b_value = 0
            if a.startswith("thedate"):
                a_value += 10
            if b.startswith("thedate"):
                b_value += 10
            return cmp(a_value, b_value)

        if params is None:
            params = dict()
        date_obj_range = get_date_range(
            params.get("time_range"), days=1, offset=0
        )
        filter_dict = DataProcessor.make_time_range_filter_dict(
            date_obj_range, group_by_field_ext
        )
        for k, v in params.items():
            if k != "time_range":
                filter_dict[k] = v
        # 查询无过滤条件的结果
        # where
        where_str = " where "
        where_list = DataProcessor.make_where_list(filter_dict)
        where_list = sorted(
            where_list, cmp=thedate_first, key=None, reverse=True
        )
        where_str += u" and ".join(where_list)
        select_fields = group_field.split(',') if group_field else []
        select_fields.extend(
            [value_field_str, group_by_field_ext, "max(_ab_delay_) as delay"]
        )
        select_fields_str = ",".join(select_fields)

        group_fields_list = group_field.split(',') if group_field else []
        group_fields_list.append(group_by_field_ext)
        group_fields_str = ','.join([i for i in group_fields_list if i])

        sql = (u"select %s from %s %s group by %s order by %s limit 0, %s" %
              (select_fields_str, result_table_id, where_str,
               group_fields_str, group_by_field_ext, SQL_MAX_LIMIT))
        ret = query(sql)
        data = ret["list"]
        if not data:
            raise EmptyQueryException
        # process data
        series_count_info_dict = dict()
        series_name_list = list()
        x_axis_list = list()
        series_name_prefix = (u"本周期" if not series_label_show
                              else series_label_show)
        delay_info_dict = dict()
        for item in data:
            series_value_list = []
            if not group_field:
                series = series_name_prefix
            else:
                for _field in group_field.split(','):
                    series_value_list.append(
                        str("[%s: %s]" % (_field, item[_field]))
                    )
                series = "_".join(series_value_list)
                series = urllib.unquote(series)
                series = u"%s-%s" % (series_name_prefix, series)
            if series not in series_name_list:
                series_name_list.append(series)
            if series not in series_count_info_dict:
                series_count_info_dict[series] = {}
            if series not in delay_info_dict:
                delay_info_dict[series] = {}
            x_axis = str(item.get(group_by_field_ext, u" "))
            x_axis = urllib.unquote(x_axis)
            if x_axis not in x_axis_list:
                x_axis_list.append(x_axis)
            # 还原时间
            x_axis_timestamp = long(time.mktime(
                datetime.datetime.strptime(
                    x_axis, "%Y-%m-%d %H:%M:%S"
                ).timetuple())) + TIME_OFFSET / 1000
            delay_info_dict[series].setdefault(
                x_axis_timestamp,
                item.get("delay") > POINT_DELAY_SECONDS
            )
            value_count = float(item.get(value_field) or 0) / conversion
            if unit == u"*100%":
                value_count *= 100
            value_count = (round(value_count, 2)
                           if value_count and value_count != "null"
                           else 0)
            if value_count < 0.05:
                value_count = (round(value_count, 5)
                               if value_count and value_count != "null"
                               else 0)
            count = value_count
            series_count_info_dict[series].setdefault(x_axis, count)
        max_y = 0
        min_y = 10 ** 10
        # 查询带过滤条件的结果，然后合并
        if cmp_date:
            # 对比查询
            start_date, end_date = get_date_range(
                params.get("time_range"), days=1, offset=0
            )
            cmp_date = date_convert(
                cmp_date, 'datetime', _time_format='%Y-%m-%d'
            )
            day_delta = start_date.date() - cmp_date.date()
            start_date = start_date - day_delta
            end_date = end_date - day_delta
            filter_dict = DataProcessor.make_time_range_filter_dict(
                (start_date, end_date), group_by_field_ext
            )
            for k, v in params.items():
                if k != "time_range":
                    filter_dict[k] = v
            where_str = " where "
            where_list = DataProcessor.make_where_list(filter_dict)
            where_list = sorted(
                where_list, cmp=thedate_first, key=None, reverse=True
            )
            where_str += u" and ".join(where_list)
            select_fields = group_field.split(',') if group_field else []
            select_fields.extend([value_field_str, group_by_field_ext])
            select_fields_str = ",".join(select_fields)

            group_fields_list = group_field.split(',') if group_field else []
            group_fields_list.append(group_by_field_ext)
            group_fields_str = ','.join([i for i in group_fields_list if i])

            sql = (u"select %s from %s %s group by %s order by %s limit 0, %s"
                   % (select_fields_str, result_table_id, where_str,
                      group_fields_str, group_by_field_ext, SQL_MAX_LIMIT))
            ret = query(sql)
            data = ret["list"]
            if not data:
                raise EmptyQueryException
            # process data
            for item in data:
                series_value_list = []
                if not group_field:
                    series = u"上周期"
                else:
                    for _field in group_field.split(','):
                        series_value_list.append(
                            str("[%s: %s]" % (_field, item[_field]))
                        )
                    series = "_".join(series_value_list)
                    series = urllib.unquote(series)
                    series = u"上周期-%s" % series
                if series not in series_name_list:
                    series_name_list.append(series)
                if series not in series_count_info_dict:
                    series_count_info_dict[series] = {}

                x_axis = str(item.get(group_by_field_ext))
                x_axis = urllib.unquote(x_axis)
                # 还原时间
                x_axis_timestamp = long(time.mktime(
                    datetime.datetime.strptime(
                        x_axis, "%Y-%m-%d %H:%M:%S"
                    ).timetuple()) + day_delta.days * 24 * 3600)
                x_axis = datetime.datetime.fromtimestamp(
                    x_axis_timestamp
                ).strftime("%Y-%m-%d %H:%M:%S")
                if x_axis not in x_axis_list:
                    x_axis_list.append(x_axis)
                value_count = float(item.get(value_field)) / conversion
                if unit == u"*100%":
                    value_count *= 100
                value_count = (round(value_count, 2)
                               if value_count and value_count != "null"
                               else 0)
                if value_count < 0.05:
                    value_count = (round(value_count, 5)
                                   if value_count and value_count != "null"
                                   else 0)
                count = value_count
                if x_axis not in series_count_info_dict[series]:
                    series_count_info_dict[series][x_axis] = 0
                series_count_info_dict[series][x_axis] += count
        # 组合所有的数据
        series_list = list()

        x_axis_list.sort()
        delaying = False
        for series in series_name_list:
            zones = list()
            delay_start_point = None
            series_item_dict = series_count_info_dict[series]
            value_list = list()
            for x_axis in x_axis_list:
                value_list.append(series_item_dict.get(x_axis, 0))
                x_axis_timestamp = long(time.mktime(
                    datetime.datetime.strptime(
                        x_axis, "%Y-%m-%d %H:%M:%S"
                    ).timetuple())) + TIME_OFFSET / 1000
                if not delaying:
                    if delay_info_dict[series].get(x_axis_timestamp, False):
                        delaying = True
                        delay_start_point = x_axis_timestamp
                if delaying:
                    if not delay_info_dict[series].get(x_axis_timestamp, False):
                        delaying = False
                        zones.append([delay_start_point, x_axis_timestamp])


            max_y = (max(value_list)
                     if value_list and max(value_list) > max_y
                     else max_y)
            min_y = (min(value_list)
                     if value_list and min(value_list) < min_y
                     else min_y)
            series_info = {"name": series,
                           "data": value_list,
                           "x_axis_list": x_axis_list,
                           "type": 'spline',
                           "percent": []}
            series_info['count'] = series_info['data']
            if series == u"本周期":
                # 数据靠前展示
                series_info["zIndex"] = 5
            if series in delay_info_dict:
                series_info["zoneAxis"] = "x"
                series_info["zones"] = SeriesHandleManage.make_zones_option(
                    zones
                )
                series_info["delay_info"] = delay_info_dict[series]
            series_list.append(series_info)
        # process data end
        data = {
            "min_y": min_y,
            "max_y": max_y,
            "chart_type": 'spline',
            "x_axis": {'type': 'datetime', 'minRange': 3600 * 1000},
            "series": series_list,
            "show_percent": False,
            "color_list": "",
        }
        if unit != u"个":
            data["unit"] = unit if unit != u"*100%" else u"%"
        # 实时数据 , 基础性能不需要时间统计窗口，因此不需要去掉最近的一个点。
        real_time = False
        # 时间轴
        data["pointInterval"] = 5 * 1000 * 60
        data["pointStart"] = today_start_timestamp(date_obj_range[0])
        data["series"] = SeriesHandleManage.make_full_datetime_series(
            series_list,
            date_obj_range[0],
            date_obj_range[1],
            HOST_POINT_INTERVAL,
            _format="%Y-%m-%d %H:%M:%S",
            real_time=real_time,
            off_set=True
        )
        data["series_name_list"] = [s['name'] for s in series_list]
        data["echo_sql"] = ""
        return data

    @staticmethod
    def make_where_list(filter_dict):
        where_list = []
        for k, v in filter_dict.items():
            _k = k.split("__")
            if len(_k) > 2:
                raise Exception(u"无效的查询参数%s" % k)
            condition = "=" if len(_k) == 1 else CONDITION_CONFIG.get(_k[1])
            if condition is None:
                raise Exception(u"无效的过滤条件%s" % k)
            if isinstance(v, list):
                v = map(lambda x: "'%s'" % x, v)
                v = u"(%s)" % ",".join(v)
            elif isinstance(v, str):
                v = u"'%s'" % v
            elif isinstance(v, unicode):
                v = u"'%s'" % v
            where_list.append(u"%s%s%s" % (_k[0], condition, v))
        return where_list


    @staticmethod
    def make_multiple_graph_point(result_table_id, value_field, group_field,
                                  params=None, filter_str=None, monitor_id=0):
        """
        根据条件生成多条取现
        """
        group_by_field_ext = "dteventtime"

        def thedate_first(a, b):
            a = str(a)
            a_value = 0
            b = str(b)
            b_value = 0
            if a.startswith("thedate"):
                a_value += 10
            if b.startswith("thedate"):
                b_value += 10
            return cmp(a_value, b_value)

        value_field = "%s as count" % value_field
        date_obj_range = get_date_range(days=1, offset=0)
        if params and "time_range" in params:
            date_obj_range = get_date_range(
                params.get("time_range"), days=1, offset=0
            )
        filter_dict = DataProcessor.make_time_range_filter_dict(
            date_obj_range, group_by_field_ext
        )
        where_str = " where "
        where_list = DataProcessor.make_where_list(filter_dict)
        where_list = sorted(
            where_list, cmp=thedate_first, key=None, reverse=True
        )
        where_str += u" and ".join(where_list)
        where_str += (u"and (%s)" % filter_str) if filter_str else u""
        select_fields_str = ",".join(
            [value_field, group_by_field_ext] + group_field.split(',')
        ) if filter_str else ",".join([value_field, group_by_field_ext])
        select_fields_str += ",max(_ab_delay_) as delay "

        sql = (u"select %s from %s %s group by %s order by %s limit 0, %s" %
               (select_fields_str,
                result_table_id,
                where_str,
                (group_by_field_ext + "," + group_field) if filter_str
                else group_by_field_ext,
                group_by_field_ext,
                SQL_MAX_LIMIT))
        ret = query(sql)
        # process data
        data = ret["list"]
        if not data:
            raise EmptyQueryException
        # process data
        series_name_list = []
        series_count_info_dict = {}
        x_axis_list = []
        delay_info_dict = {}
        for item in data:
            series_value_list = []
            if filter_str:
                for _field in group_field.split(','):
                    series_value_list.append(
                        u"[%s: %s]" % (
                            get_desc_by_field(result_table_id, _field),
                            item[_field]))
                series = "_".join(series_value_list)
            else:
                series = u"总览"
            series = urllib.unquote(series)
            if series not in series_name_list:
                series_name_list.append(series)
            if series not in series_count_info_dict:
                series_count_info_dict[series] = {}
            if series not in delay_info_dict:
                delay_info_dict[series] = {}

            x_axis = str(item.get(group_by_field_ext, u" "))
            x_axis = urllib.unquote(x_axis)
            if x_axis not in x_axis_list:
                x_axis_list.append(x_axis)
            value_count = float(item.get("count"))
            value_count = (round(value_count, 2)
                           if value_count and value_count != "null"
                           else 0)
            if value_count < 0.05:
                value_count = (round(value_count, 5)
                               if value_count and value_count != "null"
                               else 0)
            count = value_count
            series_count_info_dict[series].setdefault(x_axis, count)
            delay_info_dict[series].setdefault(
                x_axis,
                item.get("delay") > POINT_DELAY_SECONDS
            )
        # 组合所有的数据
        series_list = list()
        max_y = 0
        min_y = 10 ** 10
        x_axis_list.sort()
        for series in series_name_list:
            delay_info = {}
            zones = []
            delaying = False
            series_item_dict = series_count_info_dict[series]
            value_list = list()
            delay_start_point = None
            for x_axis in x_axis_list:
                x_axis_timestamp = long(time.mktime(
                    datetime.datetime.strptime(
                        x_axis, "%Y-%m-%d %H:%M:%S"
                    ).timetuple())) + TIME_OFFSET / 1000
                delay_info.setdefault(
                    x_axis_timestamp,
                    delay_info_dict[series].get(x_axis, False)
                )
                if not delaying:
                    if delay_info_dict[series].get(x_axis, False):
                        delaying = True
                        delay_start_point = x_axis_timestamp
                if delaying:
                    if not delay_info_dict[series].get(x_axis, False):
                        delaying = False
                        zones.append([delay_start_point, x_axis_timestamp])
                value_list.append(series_item_dict.get(x_axis, 0))

            max_y = max(value_list) if value_list and max(value_list) > max_y else max_y
            min_y = min(value_list) if value_list and min(value_list) < min_y else min_y
            series_info = {"name": series,
                           "data": value_list,
                           "x_axis_list": x_axis_list,
                           "type": 'spline',
                           "percent": []}
            series_info['count'] = series_info['data']
            if zones:
                series_info["zoneAxis"] = "x"
                series_info["zones"] = SeriesHandleManage.make_zones_option(
                    zones
                )
                series_info["delay_info"] = delay_info
            series_list.append(series_info)
        # process data end
        data = {
            "min_y": min_y,
            "max_y": max_y,
            "chart_type": 'spline',
            "x_axis": {'type': 'datetime', 'minRange': 3600 * 1000},
            "series": series_list,
            "show_percent": False,
            "color_list": "",
        }
        real_time = True
        # 时间轴
        data["pointInterval"] = 5 * 1000 * 60
        data["pointStart"] = today_start_timestamp(date_obj_range[0])
        try:
            from monitor.performance.models import Monitor
            monitor = Monitor.objects.get(id=monitor_id)
            step = get_time_step(
                result_table_id, monitor.generate_config_id
            ) * 1000
        except Exception, e:
            step = get_time_step(result_table_id, False) * 1000
        data["series"] = SeriesHandleManage.make_full_datetime_series(
            series_list,
            date_obj_range[0],
            date_obj_range[1],
            step,
            _format="%Y-%m-%d %H:%M:%S",
            real_time=real_time
        )
        data["series_name_list"] = [s['name'] for s in series_list]
        data["echo_sql"] = ""
        return data

class SeriesHandleManage(object):
    """
    series 列表数据处理
    """

    @staticmethod
    def make_percent_series(series_list):
        # 将通用的series变成带百分比的series
        for series in series_list:
            series['data'] = series['percent']
        return series_list

    @staticmethod
    def make_datetime_series(series_list, _format="%Y%m%d%H%M",
                             real_time=True):
        # 将通用的series变成带时间的series
        for series in series_list:
            new_data_list = []
            new_x_axis_list = []
            i = 0
            series_count = (len(series["x_axis_list"]) - 1
                            if real_time
                            else len(series["x_axis_list"]))
            # 这里将最后一个数据点清除，因为可能没有统计完毕，造成图表波动过大。
            while i < series_count:
                # 将百分比变成y轴
                x_axis = str(series["x_axis_list"][i])
                y = series['data'][i]
                if isinstance(x_axis, datetime.datetime):
                    x_axis = x_axis.strftime(_format)
                new_x_axis_list.append(time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.strptime(x_axis, _format)
                ))
                _datetime = datetime.datetime.strptime(x_axis, _format)
                x_axis = int(
                    time.mktime(_datetime.timetuple())
                ) * 1000 + TIME_OFFSET
                new_data_list.append([x_axis, y])
                i += 1
            series["data"] = new_data_list
            series["x_axis_list"] = new_x_axis_list
            # del series["name"]
            del series["percent"]
        return series_list

    @staticmethod
    def make_full_datetime_series(series_list, start_date, end_date, step,
                                  _format="%Y%m%d%H%M", real_time=True,
                                  off_set=True):
        start_timestamp = int(time.mktime(start_date.timetuple())) * 1000
        end_timestamp = int(time.mktime(end_date.timetuple())) * 1000
        range_iter = get_timestamp_range_list(
            start_timestamp, end_timestamp, step
        )
        time_offset = TIME_OFFSET if off_set else 0
        # 将series变成全天时间series，未到的时间点用None填充
        for series in series_list:
            new_data_list = []
            new_x_axis_list = []
            i = 0
            series_count = len(series["x_axis_list"])
            if series_count > 0:
                last_timestamp = int(time.mktime(date_convert(series["x_axis_list"][-1], 'datetime', _time_format=_format).timetuple())) * 1000
                if time.time() * 1000 - last_timestamp < step:
                    series_count -= 1
            while i < series_count:
                # 将百分比变成y轴
                x_axis = str(series["x_axis_list"][i])
                y = series['data'][i]
                if isinstance(y, list):
                    y = y[1]
                if isinstance(x_axis, datetime.datetime):
                    x_axis = x_axis.strftime(_format)
                new_x_axis_list.append(
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.strptime(x_axis, _format)
                    ))
                _datetime = datetime.datetime.strptime(x_axis, _format)
                x_axis = int(
                    time.mktime(_datetime.timetuple())) * 1000 + time_offset
                new_data_list.append([x_axis, y])
                i += 1
            # 插入未出现的时间序列
            none_date_list = list()
            none_x_axis_list = list()
            for point in range_iter:
                x_axis_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(point / 1000)
                )
                if x_axis_str not in new_x_axis_list:
                    none_x_axis_list.append(x_axis_str)
                    none_date_list.append([point + time_offset, None])
            new_data_list += none_date_list
            new_x_axis_list += none_x_axis_list
            new_x_axis_list.sort()
            series["data"] = sorted(new_data_list, key=lambda x: x[0])
            series["x_axis_list"] = new_x_axis_list
            if "percent" in series:
                del series["percent"]
        return series_list


    @staticmethod
    def make_zones_option(zones):
        zone_list = []
        for zone in zones:
            zone_list.append({
                "value": zone[0] * 1000
            })
            zone_list.append({
                "value": zone[1] * 1000,
                "color": POINT_DELAY_COLOR
            })
        return zone_list

def get_timestamp_range_list(start_time_stamp, end_time_stamp, step):
    return range(start_time_stamp, end_time_stamp, step)


def _query(sql):
    logger.info("BKSQL QUERY: %s", sql)
    args = {
        "sql": sql
    }
    args.update(INTERFACE_COMMON_PARAMS)
    args['bk_token'] = get_bk_token()
    data_query_url = DATA_API+"get_data"
    r = requests.post(
        data_query_url,
        data=json.dumps(args),
        timeout=16,
        headers={'content-type': 'application/json'}
    )
    r.raise_for_status()
    if not r.json()["result"]:
        raise Exception(r.json()["message"])
    res = r.json()["data"]
    logger.debug("BKSQL QUERY RESULT: %s", res)
    return res


def query(sql):
    try:
        return _query(sql)
    except Exception, e:
        if ((e.message.startswith(u"获取表") and u"请确认表是否创建成功" in e.message)) or \
           (e.message.startswith(u'Result table的物理表不存在')):
            raise TableNotExistException(e)
        raise SqlQueryException(e)


def get_data(result_table_id, monitor_field,
             dimensions=None, method="sum",
             date=arrow.now().format("YYYYMMDD"),
             conversion=1):
    dimensions = dimensions or {}
    ignore_list = ["cloud_id", "biz_id", "alarm_source_id", "alarm_attr_id"]
    dimensions["thedate"] = date
    where_sql = " and ".join(
        ["%s='%s'" % (k, v)
         for k, v in dimensions.items() if k not in ignore_list]
    )
    sql = (
        "select %(method)s(%(monitor_field)s) as _value_, dteventtime "
        "from %(result_table_id)s "
        "where %(where_sql)s "
        "group by dteventtime "
        "limit %(SQL_MAX_LIMIT)s") % dict(
            method=method,
            monitor_field=monitor_field,
            result_table_id=result_table_id,
            where_sql=where_sql,
            SQL_MAX_LIMIT=SQL_MAX_LIMIT
    )
    result = _query(sql)
    return [
        [
            arrow.get(data["dteventtime"])
            .replace(tzinfo="local").timestamp*1000,
            round(float(data["_value_"]) / conversion, 2),
        ]
        for data in result["list"]
    ]


def date_convert(_date,_format,_time_format='%Y-%m-%d %H:%M:%S'):
    try:
        if (type(_date) == type(datetime.datetime.now()) or
                    type(_date) == type(datetime.date.today())):
            if _format == 'utc':
                return datetime2utc(_date,_time_format)

        elif type(_date) == type('') or type(_date) == type(u''):
            if _format == 'datetime':
                return str2datetime(_date,_time_format)
            elif _format == 'date':
                return str2date(_date, '%Y-%m-%d')
            elif _format == 'utc':
                return str2utc(_date,_time_format)

        elif type(_date) == type(1) or type(_date) == type(long(1)):
            if _format == 'datetime':
                return utc2datetime(_date,_time_format)
            elif _format == 'date':
                return utc2date(_date,_time_format)

        return _date
    except Exception,e:
        return ''


# 字符串转datetime
def str2datetime(_str,_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(_str,_format)


def str2date(_str,_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(_str,_format).date()


def str2utc(_str,_format='%Y-%m-%d %H:%M:%S'):
    """
    字符串转UTC
    """
    _datetime = datetime.datetime.strptime(_str,_format)
    return int(time.mktime(_datetime.timetuple()))


def datetime2utc(_datetime,_format='%Y-%m-%d %H:%M:%S'):
    """
    datetime转UTC
    """
    return int(time.mktime(_datetime.timetuple()))


def utc2datetime(_utc,_format='%Y-%m-%d %H:%M:%S'):
    """
    UTC转datetime
    """
    return time.strftime(_format,time.localtime(int(_utc)))


def utc2date(_utc,_format='%Y-%m-%d %H:%M'):
    """
    UTC转date
    """
    return time.strftime(_format,time.localtime(int(_utc)))


def get_field_by_desc(rt_id, desc):
    from monitor.models import DataResultTableField
    field_objs = DataResultTableField.objects.filter(
        result_table_id=rt_id, desc=desc
    )
    if field_objs:
        field_objs = field_objs[0]
    else:
        return desc
    return field_objs.field


def get_date_range(time_range=None, **kwargs):
    """
    :param time_range: <datetime.date>
    """
    days = kwargs.get("days", 7)
    offset = kwargs.get("offset", 0)
    if not time_range:
        return get_default_time_range(days, offset)
    else:
        time_range = time_range.replace('&nbsp;', " ")
    start, end = [i.strip() for i in time_range.split(u'--')]
    start = date_convert(start, 'datetime', _time_format='%Y-%m-%d %H:%M')
    if not start:
        return get_default_time_range(days, offset)
    date_type = kwargs.get("date_type", "datetime")
    if date_type == "date":
        end = date_convert(
            end, 'datetime', _time_format='%Y-%m-%d %H:%M'
        ) + datetime.timedelta(1)
    else:
        end = date_convert(end, 'datetime', _time_format='%Y-%m-%d %H:%M')
    return start, end


def get_default_time_range(days=7, offset=0):
    if days + offset < 1:
        return (datetime.date.today(),
                datetime.date.today() + datetime.timedelta(1))
    return (datetime.date.today() - datetime.timedelta(days+offset-1),
            datetime.date.today() + datetime.timedelta(1-offset))


def get_time_step(rt_id, generate_config_id):
    from monitor.models import DataResultTable
    try:
        if generate_config_id is False:
            obj = DataResultTable.objects.filter(result_table_id=rt_id)[0]
        else:
            obj = DataResultTable.objects.get(
                result_table_id=rt_id, generate_config_id=generate_config_id
            )
        return obj.count_freq
    except DataResultTable.DoesNotExist:
        return 60


def get_time_range(datetime_obj):
    _date = datetime_obj.date()
    _date_str = _date.strftime("%Y-%m-%d")
    return get_time_range_by_datestr(_date_str)


def get_time_range_by_datestr(datestr):
    return "%s 00:00 -- %s 23:59" % (datestr, datestr)


def make_where_list(filter_dict):
    """
    生成查询过滤条件
    """
    where_list = []
    for k, v in filter_dict.items():
        _k = k.split("__")
        if len(_k) > 2:
            raise Exception(u"无效的查询参数%s" % k)
        condition = "=" if len(_k) == 1 else CONDITION_CONFIG.get(_k[1])
        if condition is None:
            raise Exception(u"无效的过滤条件%s" % k)
        if isinstance(v, list):
            v = map(lambda x: "'%s'" % x, v)
            v = u"(%s)" % ",".join(v)
        elif isinstance(v, str):
            v = u"'%s'" % v
        elif isinstance(v, unicode):
            v = u"'%s'" % v
        where_list.append(u"%s%s%s" % (_k[0], condition, v))
    return where_list


@web_cache(60 * 3)
def get_field_results(result_table_id, field, ext_filter_dict=None,
                      time_range=None):
    """
    获取时间范围内维度字段取值
    缓存3分钟。
    :return:
    """
    filter_dict = {} if ext_filter_dict is None else ext_filter_dict
    if time_range is None:
        time_range = get_default_time_range(1, 0)
    else:
        time_range = get_date_range(time_range, days=1, offset=0)
    time_range = (time_range[0].strftime("%Y%m%d"),
                  (time_range[1] + datetime.timedelta(1)).strftime("%Y%m%d"))
    filter_dict['thedate__gte'], filter_dict['thedate__lt'] = time_range
    where_sql = " where " if filter_dict else ""
    where_list = make_where_list(filter_dict)
    where_sql += u" and ".join(where_list)
    sql = ("select %s from %s %s group by %s limit 0, 1000" %
           (field, result_table_id, where_sql, field))
    try:
        ret = query(sql)
        data = ret["list"]
    except Exception, e:
        data = []
    field_list = field.split(",")
    if len(field_list) == 1:
        values = [d[field] for d in data]
    else:
        values = []
        for d in data:
            row = [d[f.strip()] for f in field_list]
            values.append(row)
    return values


def get_field_values_options(result_table_id, field, ext_filter=None,
                             time_range=None):
    results = []
    ext_filter = ext_filter or {}
    values = get_field_results(
        result_table_id, field,
        ext_filter_dict=ext_filter,
        time_range=time_range
    )
    results.extend(values)
    results = list(set(filter(lambda r: r != 'null', results)))
    data = [{'id': "", 'text': "所有"}]
    origin_data = []
    for _id in results:
        origin_data.append({'id': _id, 'text': str(_id)})
    data.extend(sorted(origin_data, key=lambda x: x['text']))
    return data


def get_desc_by_field(rt_id, field):
    from monitor.models import DataResultTableField
    field_objs = DataResultTableField.objects.filter(
        result_table_id=rt_id, field=field
    ).exclude(desc=None)
    if field_objs:
        field_objs = field_objs[0]
    else:
        return field
    return field_objs.desc or field_objs.alias_name