# coding=utf-8
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import re
from requests.exceptions import Timeout
from common.log import logger
from monitor.constants import JA_API, MSG_API, DATA_API, enum
from utils.requests_utils import custom_requests, requests_get

# 同步数据源信息

SYNC_DS_URL = JA_API + 'monitor/source_custom_couplein'
# 下发IP配置
SYNC_IPS_URL = JA_API + 'monitor/publish_collect_config'
# 查询IP下发配置状态
QUERY_IP_STATUS_URL = JA_API + 'monitor/query_collect_status/'
# 查询IP上报状态
QUERY_IP_REPORT_STATUS_URL = JA_API + 'monitor/query_ip_report_status/'
# 获取关联监控项
QUERY_DS_MONITORS_URL = JA_API + 'monitor/monitors/'
# 获取数据明细
QUERY_DS_DATA_URL = DATA_API + 'get_data'
# 获取配置选项
QUERY_OPTIONS_URL = MSG_API + 'get_{config_name}'

CONFIG_NAME_MAP = {
    'condition_op': 'condition_operator',
    'field_type': 'field_type',
    'file_frequency': 'file_frequency',
    'data_encode': 'encoding',
    'sep': 'field_delimiter'
}

DS_STATUS = enum(
    CREATE='create',
    STOP='stop',
    NORMAL='normal',
    STOPPED='stopped',
    EXCEPTION='exception',
    DELETE='delete',
)


class Datasource(models.Model):
    """
    数据源表结构
    """
    STATUS_CHOICES = (
        ('create', u'接入中'),
        ('stop', u'停用中'),
        ('normal', u'正常'),
        ('stopped', u'停用'),
    )
    cc_biz_id = models.CharField(u"cc业务id", max_length=30)
    data_set = models.CharField(u'数据源表名', max_length=100)
    data_desc = models.CharField(u'数据源中文名', max_length=100)
    data_json = models.TextField(u'数据源json数据')
    status = models.CharField(u'数据源状态',
                              max_length=20,
                              choices=STATUS_CHOICES,
                              default=DS_STATUS.CREATE)
    has_exception = models.BooleanField(u'是否有异常IP', default=False)
    creator = models.CharField(u'创建人', max_length=50)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_user = models.CharField(u'最新修改人', max_length=50, default='')
    update_time = models.DateTimeField(u'最近更新时间', auto_now=True)
    # 后台侧的数据
    data_id = models.CharField(u"后台侧数据源id", max_length=100, default='')
    result_table_id = models.CharField(u"后台侧表id", max_length=100, default='')

    def __uincode__(self):
        return '%s[%s]' % (self.data_desc, self.data_set)

    class Meta:
        verbose_name = u"数据源"
        verbose_name_plural = u"数据源"
        unique_together = ('cc_biz_id', 'data_set')

    def sync_to_server(self):
        """
        同步数据源到后台
        POST
        {
            "biz_id": "21",
            "data_set": "test_hydra1",
            "data_desc": "hydra测试自定义接入1",
            "ips": "10.104.35.171",
            "log_path": "/data/home/monitor/var/log/pizza.log",
            "file_frequency": "1",
            "data_encode": "UTF-8",
            "sep": " ",
            "conditions": "[{\"index\": \"1\", \"logic_op\": \"and\", \"value\": \"2\", \"op\": \"&gt;\"}, {\"index\": \"2\", \"logic_op\": \"and\", \"value\": \"3\", \"op\": \"&lt;\"}]",
            "fields": "[{\"index\": \"1\", \"name\": \"svr_ip\", \"time_zone\": \"\", \"time_format\": \"\", \"alis\": \"\\u670d\\u52a1\\u5668\\u7684IP\", \"type\": \"string\", \"description\": \"\\u670d\\u52a1\\u5668IP\"}, {\"index\": \"2\", \"name\": \"field2\", \"time_zone\": \"\", \"time_format\": \"\", \"alis\": \"\\u5b57\\u6bb52\", \"type\": \"string\", \"description\": \"\\u5b57\\u6bb52\"}, {\"index\": \"3\", \"name\": \"field3\", \"time_zone\": \"\", \"time_format\": \"\", \"alis\": \"\\u5b57\\u6bb53\", \"type\": \"string\", \"description\": \"\\u5b57\\u6bb53\"}, {\"index\": \"4\", \"name\": \"field4\", \"time_zone\": \"+8\", \"time_format\": \"5\", \"alis\": \"\\u5b57\\u6bb54\", \"type\": \"string\", \"description\": \"\\u5b57\\u6bb54\"}]"
        }
        :return:
        """
        data = json.loads(self.data_json)
        data['ips'] = ','.join(data['ips'])
        data['fields'] = json.dumps(data['fields'])
        data['conditions'] = json.dumps(data['conditions'])
        data['biz_id'] = self.cc_biz_id
        data['data_id'] = self.data_id
        res = custom_requests('post', SYNC_DS_URL, data=data)
        # 记录data_id，result_table_id
        self.data_id = res['data']['data_id']
        self.result_table_id = res['data']['result_table_id']
        self.save()

    def sync_ips(self, ips, action):
        """
        下发ip配置
        @param ips: 为None时，获取当前数据源下所有
        POST
        {
            "biz_id": "21",
            "data_id": "1",
            "ips": "10.104.35.171,10.104.35.172", # 逗号分隔
            "conditions": "[{\"index\": \"1\", \"logic_op\": \"and\", \"value\": \"2\", \"op\": \"&gt;\"}, {\"index\": \"2\", \"logic_op\": \"and\", \"value\": \"3\", \"op\": \"&lt;\"}]"
            "action": "on",  # on/off: 打开/关闭
        }
        :return:
        """

        data = {}
        data['biz_id'] = self.cc_biz_id
        data['data_id'] = self.data_id
        data['conditions'] = json.dumps(
            json.loads(self.data_json)['conditions']
        )
        data['ips'] = ips
        data['action'] = action
        # 后台是同步接口，设置3秒的超时时间，超时表示成功
        try:
            res = custom_requests('post', SYNC_IPS_URL, data=data, timeout=3)
        except Timeout:
            pass

        source_data = json.loads(self.data_json)
        if action == "on":
            if ips not in source_data["ips"]:
                source_data["ips"].append(ips)
        elif action == "off":
            if ips in source_data["ips"]:
                source_data["ips"].remove(ips)
        self.data_json = json.dumps(source_data)
        self.save()

    def get_ip_list(self):
        """
        获取ip列表
        :return:
        """
        return list(AgentStatus.objects.filter(
            ds_id=self.id).exclude(status=DS_STATUS.DELETE).values_list('ip', flat=True)
        )

    def update_status(self):
        """
        更新接入状态
        :return:
        """
        # logger.info('update_status start')
        url = QUERY_IP_STATUS_URL
        res = requests_get(url, **{"biz_id": self.cc_biz_id, "data_id": self.data_id})
        # logger.info('update_status finish')
        if not res['result']:
            raise Exception('update_status false')
        for ip_info in res['data']:
            try:
                AgentStatus.objects.get(
                    ds_id=self.id,
                    ip=ip_info['ip']).update_status(ip_info['ip_op_result']
                )
            except ObjectDoesNotExist:
                logger.warning('ip not exist. ds_id: {ds_id}, ip: {ip}'.format(
                    ds_id=self.id, ip=ip_info['ip'])
                )
        # 更新数据源的状态
        self.update_ds_status()


    def update_report_status(self):
        """
        更新数据上报状态
        :return:
        """
        res = requests_get(QUERY_IP_REPORT_STATUS_URL, **{"biz_id": self.cc_biz_id, "data_id": self.data_id})
        if not res['result']:
            return
        for ip, ip_info in res['data'].items():
            if 'agent_status' not in ip_info:
                continue
            try:
                agent = AgentStatus.objects.get(ds_id=self.id, ip=ip)
                if agent.status in (DS_STATUS.CREATE, DS_STATUS.NORMAL, DS_STATUS.EXCEPTION):
                    agent.status = (DS_STATUS.NORMAL if ip_info['agent_status'] == 1
                                    else DS_STATUS.EXCEPTION)
                    if 'last_report_time' in ip_info:
                        agent.update_time = ip_info['last_report_time']
                    agent.save()
            except ObjectDoesNotExist:
                logger.warning('ip not exist. ds_id: {ds_id}, ip: {ip}'.format(
                    ds_id=self.id, ip=ip)
                )
        # 更新数据源状态
        self.update_ds_status()


    def update_ds_status(self):
        """
        更新数据源的状态
        :return:
        """
        # logger.info('update_ds_status 1')
        self.has_exception = AgentStatus.objects.filter(
            ds_id=self.id, status=DS_STATUS.EXCEPTION
        ).exists()
        # logger.info('update_ds_status 2')
        if self.status == DS_STATUS.CREATE and not AgentStatus.objects.filter(
                ds_id=self.id, status=DS_STATUS.CREATE).exists():
            # 接入中
            self.status = DS_STATUS.NORMAL
        elif self.status == DS_STATUS.STOP and not AgentStatus.objects.filter(
                ds_id=self.id, status=DS_STATUS.STOP).exists():
            self.status = DS_STATUS.STOPPED
        # logger.info('update_ds_status 3')
        # self.save()
        self.save(update_fields=['has_exception', 'status'])
        # self.save(force_update=True)
        # Datasource.objects.filter(id=self.id).update(has_exception=self.has_exception, status=self.status)
        # logger.info('update_ds_status 4')


    def get_detail_data(self, date, page, page_size):
        """
        获取数据明细
        :return:
        """
        # 组装查询参数
        where_clause = ''
        if date != '':
            if not re.match(r'\d{4}-\d{2}-\d{2}', date):
                raise Exception('Invalid date: %s' % date)
            where_clause = 'where dtEventTime like "{0}%"'.format(date)
        offset = (int(page) - 1) * int(page_size)

        # 混合云版保证rt_id中的业务正确
        from utils.trt import trans_bkcloud_rt_bizid
        rt_id = trans_bkcloud_rt_bizid(self.result_table_id)

        sql = 'select * from %s %s order by dtEventTime desc limit %s, %s' % (
            rt_id, where_clause, offset, page_size
        )
        res = custom_requests('post', QUERY_DS_DATA_URL, data={'sql': sql})
        res['data']['total'] = res['data'].pop('totalRecords')
        return res

    def get_detail_data_total(self, date):
        """
        获取数据明细总数
        :param date:
        :return:
        """
        # 组装查询参数
        where_clause = ''
        if date != '':
            if not re.match(r'\d{4}-\d{2}-\d{2}', date):
                raise Exception('Invalid date: %s' % date)
            where_clause = 'where dtEventTime like "{0}%"'.format(date)
        sql = 'select count(*) as total from %s %s' % (
            self.result_table_id, where_clause
        )
        res = custom_requests('post', QUERY_DS_DATA_URL, data={'sql': sql})
        try:
            res['data'] = res['data']['list'][0]['total']
        except IndexError:
            res['data'] = 0
        return res

    def get_monitors(self):
        """
        获取关联监控项
        :return:
        """
        res = requests_get(QUERY_DS_MONITORS_URL, **{"stat_source_info__contains": self.result_table_id})
        return res

    @staticmethod
    def bulid_list_data(data_qs, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        return list(data_qs[start: end])

    @staticmethod
    def validate_ip(ip):
        return re.search(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip)

    @staticmethod
    def validate_condition(condition):
        if not re.search(r'^[0-9]*$', condition['index']):
            raise Exception(u"列值只能是数字，请输入正确的列值")
        if condition['value'] == '':
            raise Exception(u"请输入条件值")

    @staticmethod
    def validate_field(field):
        if not re.search(r'^[a-zA-Z][a-zA-Z0-9_]*$', field['name']):
            raise Exception(u"请输入合法的字段名")
        if field['description'] == '':
            raise Exception(u"请输入字段的中文描述")
        if (field['alis'] != '' and
                not re.search(r'^[a-zA-Z][a-zA-Z0-9_]*$', field['alis'])):
            raise Exception(u"请输入合法的别名")
        if not Datasource.validate_option('field_type', field['type']):
            raise Exception(u"请选择字段类型")
        if not ((field['time_format'] == '' and field['time_zone'] == '') or
                (field['time_format'] == '1' and field['time_zone'] == '+8')):
            raise Exception(u"非法请求")

    @staticmethod
    def validate_ds_correct(ds_data):
        """
        校验数据合法性，和前端校验逻辑保持一致
        :param ds_data:
        :return:
        """
        if not re.search(r'^[a-zA-Z][a-zA-Z0-9_]*$', ds_data['data_set']):
            raise Exception(u"表名不合法，请遵循MySQL的数据表命名规则")
        if ds_data['data_desc'] == '':
            raise Exception(u"请输入数据源的中文名称")
        for ip in ds_data['ips']:
            if not Datasource.validate_ip(ip):
                raise Exception(u"请输入合法的IP")
        if ds_data['log_path'] == '':
            raise Exception(u"请输入日志路径")
        if not Datasource.validate_option(
                'file_frequency', ds_data['file_frequency']
        ):
            raise Exception(u"请选择日志生成频率")
        if not Datasource.validate_option(
                'data_encode', ds_data['data_encode']
        ):
            raise Exception(u"请选择字符编码")
        if not Datasource.validate_option('sep', ds_data['sep']):
            raise Exception(u"请选择数据分隔符")
        for condition in ds_data['conditions']:
            Datasource.validate_condition(condition)
        if len(ds_data['fields']) == 0:
            raise Exception(u"数据表字段定义不能为空")
        fields = []
        time_field_count = 0
        for field in ds_data['fields']:
            Datasource.validate_field(field)
            fields.append(field['name'])
            if field['alis'] != '':
                fields.append(field['alis'])
            if field['time_format'] != '':
                time_field_count += 1
        # 字段名或别名不能有重复
        if len(fields) != len(set(fields)):
            raise Exception(u"字段名或别名不能有重复")
        # 有且仅有一个时间字段
        if time_field_count != 1:
            raise Exception(u"请选择时间字段")

    @staticmethod
    def validate_ds_immutable(old_data, new_data):
        """
        校验数据源更新时，不可修改的字段
        :param old_data:
        :param new_data:
        :return:
        """
        # 编辑数据，表名、采集对象ip、字段等不能变动
        return (old_data['data_set'] == new_data['data_set'] and
                old_data['ips'] == new_data['ips'] and
                Datasource.validate_fields_immutable(
                    old_data['fields'], new_data['fields']))

    @staticmethod
    def validate_fields_immutable(old_fields, new_fields):
        """
        校验字段配置：字段数量、名称、别名、类型不能修改
        :param old_fields:
        :param new_fields:
        :return:
        """
        if len(old_fields) == len(new_fields):
            for i, old_field in enumerate(old_fields):
                # 字段名称、别名、类型不能修改
                if not (old_field['name'] == new_fields[i]['name'] and
                        old_field['alis'] == new_fields[i]['alis'] and
                        old_field['type'] == new_fields[i]['type']):
                    return False
        return True

    @staticmethod
    def deco_ds_data(ds_data):
        """
        数据加工，ips、field里面增加额外数据
        :param ds_data:
        :return:
        """
        for condition in ds_data['conditions']:
            condition['logic_op'] = 'and'
            condition['op'] = '='
        for index, field in enumerate(ds_data['fields']):
            field['index'] = index + 1
            field['checked'] = 1

    @staticmethod
    def get_select_options(config_name):
        """
        获取下拉框选项
        :param config_name:
        :return: [{
                    display: "=",
                    value: "="
                }],
        """
        url = QUERY_OPTIONS_URL.format(
            config_name=CONFIG_NAME_MAP[config_name]
        )
        return requests_get(url)['data']


    @staticmethod
    def validate_option(config_name, option):
        """
        校验下拉框选项
        :param config_name:
        :param option:
        :return:
        """
        options = Datasource.get_select_options(config_name)
        option_list = [item['value'] for item in options]
        return option in option_list

    @staticmethod
    def get_processing_ds():
        """
        获取正在接入中的ds
        IP状态为：接入中、停用中、剔除中
        :return:
        """
        ds_id_list = AgentStatus.objects.filter(
            status__in=(DS_STATUS.CREATE, DS_STATUS.STOP, DS_STATUS.DELETE)
        ).values_list('ds_id', flat=True).distinct()
        return Datasource.objects.filter(cc_=ds_id_list)

    @staticmethod
    def get_normal_ds():
        """
        获取已经接入的ds
        IP状态为：正常、异常
        :return:
        """
        ds_id_list = AgentStatus.objects.filter(
            status__in=(DS_STATUS.NORMAL, DS_STATUS.EXCEPTION)
        ).values_list('ds_id', flat=True).distinct()
        return Datasource.objects.filter(id__in=ds_id_list)


class AgentStatus(models.Model):
    STATUS_CHOICES = (
        ('create', u'接入中'),
        ('stop', u'停用中'),
        ('normal', u'正常'),
        ('stopped', u'停用'),
        ('exception', u'异常'),
        ('delete', u'剔除中'),
    )
    ds_id = models.IntegerField(u"数据源ID")
    ip = models.CharField(u"采集对象IP", max_length=20)
    status = models.CharField(u"agent状态",
                              max_length=20,
                              default=DS_STATUS.CREATE,
                              choices=STATUS_CHOICES)
    creator = models.CharField(u'创建人', max_length=50)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"最近一次上报时间",
                                       null=True,
                                       blank=True)

    class Meta:
        unique_together = ['ds_id', 'ip']
        verbose_name = u"IP状态"
        verbose_name_plural = u"IP状态"

    def update_status(self, status):
        """
        更新接入状态
        :param status:
            fail 执行失败
            pending 执行中
            suc 执行成功

        :return:
        """
        if status == 'suc':
            if self.status == DS_STATUS.CREATE:
                self.status = DS_STATUS.NORMAL
            elif self.status == DS_STATUS.STOP:
                self.status = DS_STATUS.STOPPED
            elif self.status == DS_STATUS.DELETE:
                # 剔除成功后删除ip
                self.delete()
                return
        elif status == 'fail':
            self.status = DS_STATUS.EXCEPTION
        self.save()

    def update_report_status(self, update_time, status):
        self.update_time = update_time
        self.status = status
        self.save()

    @staticmethod
    def bulid_list_data(data_qs, page, page_size):
        start = (page - 1) * page_size
        end = start + page_size
        return list(data_qs[start: end])