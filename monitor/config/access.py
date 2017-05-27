# -*- coding: utf-8 -*-
"""
@desc:
"""
import json
from django.conf import settings

from common.log import logger
from monitor import constants
from monitor.models import (DataCollector, DataGenerateConfig, DataResultTable,
                            DataResultTableField)
from monitor.performance.models import Monitor
from utils import trt
from utils.common_utils import safe_int


class BaseAccess(object):

    check_list = []

    def __init__(self, param):
        self.param = param
        self.check_param()

    def check_param(self):
        for key in self.check_list:
            if not self.param.get(key, ""):
                raise Exception(u"参数不能为空: %s" % key)
        if len(self.param.get("monitor_name", "")) > 20:
            raise Exception(u"监控名称不能超过20字符")

    def access(self):
        """
        监控接入主流程
        """
        raise NotImplementedError(u'subclasses of BaseAccess '
                                  u'must provide a access() method')

    @staticmethod
    def generate_data_format(biz_id, data_id, time_field,
                             dim_fields, count_field='*'):
        """
        接入生成模版变量data_format
        """
        data_format = []
        columns = trt.list_fields(data_id=data_id)["data"]
        for column in columns:
            column_name = column['name']
            if column_name == time_field:
                data_format.append('timestamp')
            elif column_name in dim_fields:
                data_format.append(column['name'])
            elif column_name == count_field:
                data_format.append(column['name'])
            else:
                data_format.append('_')
        return data_format


class DataAccess(BaseAccess):

    def __init__(self, param):
        super(DataAccess, self).__init__(param)

        self.source_data_type = self.param.get("scenario", "custom")
        self.monitor_field = self.param['count_field']["name"]

    def check_param(self):
        self.check_list = [
            "biz_id", "src_type",
            "result_table_id", "monitor_name",
            "count_field"]
        super(DataAccess, self).check_param()

    def access(self):
        access_params = {
            "biz_id": self.param['biz_id'],
            "title": self.param.get('monitor_name', ''),
            "monitor_target": self.monitor_field,
            "target_result_table_id": self.param['result_table_id'],
            "agg_method": self.param.get('count_method', ''),
            "count_freq": self.param.get('count_freq', ''),
            "dimensions": '|'.join([field.get('id', '') for field in
                                    self.param.get('dimension_fields', [])])
        }
        # create monitor
        monitor = Monitor.create(self.param['biz_id'],
                                 "custom",
                                 "custom",
                                 self.param['monitor_name'],
                                 self.param['monitor_desc'],
                                 "custom",
                                 self.param['result_table_id'],
                                 self.monitor_field,
                                 access_params=access_params)

        # add kafka if result table dont have it
        if settings.RUN_MODE != "DEVELOP":
            try:
                result_table = trt.get_result_table(
                    id=self.param['result_table_id'])
            except Exception, e:
                logger.exception(e)
                raise Exception(u"结果表不存在")

            if 'kafka' not in result_table['storages']:
                try:
                    trt.add_storage(
                        result_table_id=result_table['id'], storage='kafka')
                except Exception, e:
                    raise Exception(u"创建作业（添加存储）失败")
        # parse result table and add result table info into config db
        parse_result_table(
            biz_id=self.param['biz_id'],
            generate_config_id=0,
            result_table_id=self.param['result_table_id']
        )

        return monitor

    def check_monitor_exist(self):
        monitors = Monitor.objects.filter(
            biz_id=self.param['biz_id'],
            is_deleted=False
        )
        for m in monitors:
            if (m.monitor_result_table_id == self.param['result_table_id'] and
                        m.monitor_field == self.monitor_field):
                return dict(result=True, id=m.id)
        return dict(result=False, id=0)


class DataSetAccess(BaseAccess):

    def __init__(self, param):

        super(DataSetAccess, self).__init__(param)

        dimension_fields = [d["id"] for d in param["dimension_fields"]]

        time_field = trt.get_data_id(
            biz_id=param['biz_id'],
            data_id=param['dataid'])["data"]

        processor = constants.DATA_FORMAT.get(param['data_format_id'],
                                              'parse_json')
        if processor == 'parse_json':
            data_format = []
        else:
            data_format = self.generate_data_format(
                param['biz_id'], param['dataid'],
                time_field["time_field_name"], dimension_fields,
                param['count_field']['name']
            )

        self.template_id = 4 if param['count_method'] == 'avg' else 2
        self.template_vars = dict(
            time_field=time_field["time_field_name"],
            time_field_type=time_field["time_format_id"],
            processor=processor,
            data_format=data_format,
            dimension_fields=param["dimension_fields"],
            count_method=param['count_method'],
            count_freq=param['count_freq'],
            count_field=param['count_field'])
        self.source_data_type = self.param.get("scenario", "custom")
        self.monitor_field = ("count" if param["count_method"] == "count"
                              else param['count_field']["name"])

    def access(self):
        """
        监控接入主流程
        """
        # 保存数据源接入信息
        collector = DataCollector.objects.create(
            biz_id=self.param['biz_id'],
            source_type='data',
            collector_config=json.dumps(self.param),
            data_type=self.source_data_type,
            data_id=self.param['dataid'],
            data_set=self.param['dataset'])

        # 调用后台的接入接口， 获得接入的后台id
        source_type = ('data_id' if 'dataid' in self.param.keys()
                       else 'result_table')
        if source_type == 'data_id':
            source_id = self.param.get('dataid', 0)
        else:
            source_id = self.param.get('result_table_id', '')

        # 生成接入相关的配置access_params
        if source_type == 'data_id':
            source_id = "%s_%s" % (self.param['biz_id'], self.param['dataset'])
        rstable_id = source_id

        dimensions = '|'.join(
            [field['id'] for field in self.param.get('dimension_fields', [])]
        )
        access_params = {
            "biz_id": self.param['biz_id'],
            "title": self.param.get('monitor_name', ''),
            "monitor_target": self.monitor_field,
            "target_result_table_id": rstable_id,
            "source_type": source_type,
            "source_id": source_id,
            "agg_method": self.param.get('count_method', ''),
            "count_freq": self.param.get('count_freq', ''),
            "dimensions": dimensions
        }

        # 保存接入配置信息
        try:
            generate_config = DataGenerateConfig.objects.create(
                biz_id=self.param['biz_id'],
                collector_id=collector.id,
                template_id=0,
                template_args=json.dumps(self.template_vars),
                job_id='',
                bksql='',
                project_id=constants.PUBLIC_ID['custom'])
        except Exception, e:
            logger.exception(e)
            raise Exception(u"创建作业配置失败")

        # create monitor
        monitor = Monitor.create(self.param['biz_id'],
                                 "custom",
                                 "custom",
                                 self.param['monitor_name'],
                                 self.param['monitor_desc'],
                                 "custom",
                                 rstable_id,
                                 self.monitor_field,
                                 generate_config_id=generate_config.id,
                                 access_params=access_params)

        parse_result_table(
            biz_id=self.param['biz_id'],
            generate_config_id=generate_config.id,
            result_table_id=rstable_id,
            dimensions=self.param.get('dimension_fields', []),
            monitor=monitor
        )

        return monitor

    def check_param(self):
        self.check_list = [
            "biz_id", "src_type", "count_freq",
            "monitor_name", "count_method",
            "count_field"]

        super(DataSetAccess, self).check_param()

    def check_monitor_exist(self):
        dimension_fields = [d["id"] for d in self.param["dimension_fields"]]
        for m in Monitor.objects.filter(biz_id=int(self.param["biz_id"])):
            rstable = m.result_table
            if safe_int(m.generate_config_id, 0) == 0:
                data_id = 0
            else:
                data_id = DataCollector.objects.get(
                    id=rstable.generate_config.collector_id).data_id
            m_dimension_fields = [f.field for f in m.dimensions]
            if (int(self.param["biz_id"]) == m.biz_id and
                    self.monitor_field == m.monitor_field and
                    self.param["count_method"] == m.count_method and
                    int(self.param["count_freq"]) == rstable.count_freq and
                    int(self.param['dataid']) == data_id and
                    len(set(dimension_fields) - set(m_dimension_fields)) == 0):
                return dict(result=True, id=m.id)
        return dict(result=False, id=0)


def parse_result_table(biz_id, generate_config_id, result_table_id,
                       dimensions=None, monitor=None):
    result_table = trt.get_result_table(id=result_table_id)['data']
    try:
        parse_table(
            biz_id, generate_config_id, result_table,
            "head", dimensions, monitor
        )
    except Exception, e:
        logger.exception(e)
        raise Exception(u"解析结果表失败")


def parse_table(biz_id, generate_config_id, result_table, parents,
                dimensions=None, monitor=None):
    count_freq = result_table['count_freq']
    if count_freq < 60:
        count_freq = 60
    if monitor is not None:
        try:
            source_info = json.loads(monitor.stat_source_info)
            count_freq = source_info.get('count_freq', 60)
        except Exception, e:
            pass

    if dimensions is not None:
        dimension_fields = [field['id'] for field in dimensions]
    if DataResultTable.objects.filter(
            result_table_id=result_table["id"],
            generate_config_id=generate_config_id).exists():
        return True
    DataResultTable.objects.create(
        result_table_id=result_table['id'],
        biz_id=biz_id,
        table_name=result_table['id'].split('_', 1)[1],
        generate_config_id=generate_config_id,
        count_freq=count_freq,
        parents=json.dumps(result_table.get("parents", [parents])))
    for index, field in enumerate(result_table['fields']):
        is_dimension = field.get('is_dimension', False)
        if dimensions is not None:
            is_dimension = field['field'] in dimension_fields
        DataResultTableField.objects.create(
            result_table_id=result_table['id'],
            generate_config_id=generate_config_id,
            field=field['field'],
            desc=field.get("description", ""),
            field_type=field['type'],
            processor=field.get('processor'),
            processor_args=field.get('processor_args'),
            is_dimension=is_dimension,
            origins=json.dumps(field.get('origins', '')),
            field_index=index)
    for rstable in result_table.get('z=====> children', []):
        parse_table(biz_id, generate_config_id, rstable, result_table["id"])
    return True
