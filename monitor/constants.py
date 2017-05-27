# -*- coding:utf-8 -*-
from django.conf import settings
from conf.default import BK_PAAS_HOST


def enum(**enums):
    return type("Enum", (), enums)

# Agent状态
AGENT_STATUS = enum(
    UNKNOWN=-1,
    ON=0,
    OFF=1,
    NOT_EXIST=2,
    NO_DATA=3
)

# 需要展示的标准属性列表
DISPLAY_STANDARD_PROPERTY_LIST = [
    "SetName",
    "ModuleName",
    "Source",
    "Operator",
    "BakOperator",
    "HostName",
    "OSName",
    "Status",
    "ZoneName",
    "Region",
    "Mem",
    "Cpu",
    "BandWidth"
]

# sql查询条件映射
CONDITION_CONFIG = {
    "lt": "<",
    "gt": ">",
    "lte": "<=",
    "gte": ">=",
    "in": " in ",
}

# 统计方法解释
VALUE_METHOD_DESC = {
    "sum": u"求和",
    "max": u"最大",
    "min": u"最小",
    "avg": u"平均",
    "count": u"count(*)",
}


# 告警策略
STRATEGY_CHOICES = (
    (1000, u"静态阈值"),
    (1001, u"同比策略（简易）"),
    (1002, u"环比策略（简易）"),
    (1003, u"同比策略（高级）"),
    (1004, u"环比策略（高级）"),
)

# 告警级别
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

# 通知方式小图标
NOTIRY_WAY_DICT = {
    'mail': u'<i class="fa fa-envelope-o text-primary data-tip" '
            u'data-html="true" data-trigger="hover" data-placement="top" '
            u'data-content="邮件"></i>',
    'wechat': u'<i class="fa fa-weixin text-success data-tip" '
              u'data-html="true" data-trigger="hover" data-placement="top" '
              u'data-content="微信"></i>',
    'sms': u'<i class="fa fa-comment-o text-success data-tip" '
           u'data-html="true" data-trigger="hover" data-placement="top" '
           u'data-content="短信"></i>',
    'im': u'<i class="iconfont text-info rtx data-tip" '
          u'data-html="true" data-trigger="hover" data-placement="top" '
          u'data-content="RTX">&#xe63e;</i>',
    'phone': u'<i class="fa fa-phone phone text-info data-tip" '
             u'data-html="true" data-trigger="hover" data-placement="top" '
             u'data-content="电话"></i>'
}
NOTIRY_WAY_NAME_DICT = {
    'mail': u'邮件',
    'wechat': u'微信',
    'sms': u'短信',
    'im': u'RTX',
    'phone': u'电话'
}

# 通知方式大图标
NOTIRY_WAY_DICT_NEW = {
    'mail': u"""
    <img class="data-tip" src="{STATIC_URL}alert/img/mail.png"
    data-html="true" data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>邮件</span>">
    """,
    'wechat': u"""
    <img class="data-tip" src="{STATIC_URL}alert/img/wechat.png"
    data-html="true" data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>微信</span>">
    """,
    'sms': u"""
    <img class="data-tip" src="{STATIC_URL}alert/img/sms.png"
    data-html="true" data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>短信</span>">
    """,
    'im': u"""
    <img class="data-tip" src="{STATIC_URL}alert/img/im.png"
    data-html="true" data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>RTX</span>">
    """,
    'phone': u"""
    <img class="data-tip" src="{STATIC_URL}alert/img/phone.png"
    data-html="true" data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>电话</span>">
    """,

}

NOTIRY_MAN_DICT = {
    'Operator': u"主负责人",
    'BakOperator': u"备份负责人",
    'Maintainers': u"运维",
    'OperationPlanning': u"运营规划",
    'PmpProductMan': u"产品",
    'PmpDBAMajor': u"DBA",
    'ProductPm': u'产品人员',
}

NOTIRY_MAN_STR_DICT = {
    'PmpProductMan': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">产品</span>
    """,
    'BakOperator': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>备份负责人</span>">备份负责人</span>
    """,
    'Operator': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>主负责人</span>">主负责人</span>
    """,
    'Maintainers': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">运维</span>
    """,
    'OperationPlanning': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">运营规划</span>
    """,
    'PmpDBAMajor': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">DBA</span>
    """,
    'responsible': u"""
    <span class="data-tip label label-default" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">额外通知人</span>
    """,
    'phone_receiver': u"""
    <span class="data-tip label label-success" data-html="true"
    data-trigger="hover" data-placement="top"
    data-content="<span class='word-break'>%s</span>">电话接收人</span>
    """
}


TRT_API = "%s/trt/" % settings.API_URL
MSG_API = "%s/databus/" % settings.API_URL
DATA_API = "%s/maple/" % settings.API_URL
JA_API = "%s/monitor/" % settings.API_URL

ALARM_COUNTS_URL = JA_API + 'alarm/alarms/cnts/'
ALARM_FREQ_URL = JA_API + 'alarm/alarms/freq_alarms'
ALARM_RECENT_URL = JA_API + 'alarm/alarms'
AGENT_STATUS_URL = JA_API + 'monitor/agent_status'


# 数据平台公共项目ID
PUBLIC_ID = {'custom': 1}

# data_format_id映射processor
DATA_FORMAT = {
    2: "parse_tlog",
    3: "split_pipe",
    4: "parse_json",
    9: "parse_json",
    10: "split_pipe",
    11: "parse_json"
}

# AlertInstance的告警维度(dimensions)
JUNGLE_SUBJECT_TYPE = {
    "cc_set": u"大区",
    "set": u"大区",
    "os": u"系统",
    "plat": u"平台",
    "ip": u"IP",
    "cc_module": u"模块",
    "_server_": "IP",
    "_path_": u"路径"
}

# 主机性能采集间隔
HOST_POINT_INTERVAL = 60 * 1000

# 数据延时判定(秒)
POINT_DELAY_SECONDS = 60 * 10
POINT_DELAY_COLOR = "#f3b760"

# 告警事件类型
ALARM_EVENT_TYPE = enum(
    alwaysAlert='alwaysAlert',
    recentAlert='recentAlert',
    recentOperate='recentOperate',
)

# 作业平台url
JOB_URL = settings.BK_JOB_URL

# agent 安装 url
AGENT_SETUP_URL = "/o/bk_agent_setup/"


#SQL最大查询条数
SQL_MAX_LIMIT = 50000
