# coding=utf-8

import json
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from common.log import logger
from monitor.datasource.models import DS_STATUS
from monitor.models import Datasource, AgentStatus
from utils import decorators
from common.mymako import render_mako_context, render_json
from account.decorators import login_exempt
from utils.common_utils import strip, convert_textarea_to_list, get_unique_list
from utils.requests_utils import RequestsResultException


@decorators.check_perm
def home(request, cc_biz_id):
    """
    首页

    :param request:
    :param cc_biz_id:
    :return:
    """
    return render_mako_context(
        request, '/monitor/datasource/home.html', {'cc_biz_id': cc_biz_id}
    )


@login_exempt
# @decorators.check_perm
def render_page(request, cc_biz_id, html):
    """
    返回页面，给前端使用

    :param request:
    :param cc_biz_id:
    :param html:
    :return:
    """
    return render_mako_context(
        request, '/monitor/datasource/%s' % html, {'cc_biz_id': cc_biz_id}
    )


@decorators.check_perm
def get_ds_list(request, cc_biz_id, page, page_size):
    """
    获取数据源列表

    :param request:
    :param cc_biz_id:
    :param page: 当前页面
    :param page_size: 每页的条数
    :return: dict
        {
            'result': True/False,
            'message': 'message',       # 提示信息
            'data': {
                'total': 100,   # 总数
                'list': [],  # 当前页的列表数据
            }
        }
    """
    keyword = request.GET.get('keyword', '')
    kwargs = {'cc_biz_id': cc_biz_id}
    if keyword != '':
        kwargs['data_desc__icontains'] = keyword
    ds_qs = Datasource.objects.filter(
        **kwargs
    ).order_by('-create_time').values(
        'id',
        'data_desc',
        'status',
        'creator',
        'create_time',
        'update_time',
        'has_exception'
    )
    total = ds_qs.count()
    ds_list = Datasource.bulid_list_data(ds_qs, int(page), int(page_size))
    # 获取关联配置项
    for ds in ds_list:
        try:
            ds['monitor_total'] = len(Datasource.objects.get(
                id=ds['id']
            ).get_monitors()['data'])
        except:
            ds['monitor_total'] = 0
    return render_json({
        'result': True,
        'message': '',
        'data': {'total': total, 'list': ds_list}
    })


@decorators.check_perm
def get_ds(request, cc_biz_id, ds_id):
    """
    获取数据源详情

    :param request:
    :param cc_biz_id:
    :param ds_id:
    :return:
    """
    try:
        ds = Datasource.objects.filter(
            cc_biz_id=cc_biz_id, id=ds_id
        ).values()[0]
        result = True
        msg = ''
        data = ds
    except ObjectDoesNotExist:
        result = False
        msg = u'数据源不存在'
        data = None
    return render_json({'result': result, 'message': msg, 'data': data})


@decorators.check_perm
def get_agent_status(request, cc_biz_id, ds_id, page, page_size):
    """
    获取数据源上报节点状态
    :param request:
    :param cc_biz_id:
    :param ds_id:
    :return:
    """
    # logger.info('get_agent_status')
    try:
        # a = datetime.datetime.now()
        # ds = Datasource.objects.get(cc_biz_id=cc_biz_id, id=ds_id)
        # 更新接入状态
        Datasource.objects.get(cc_biz_id=cc_biz_id, id=ds_id).update_status()
        # logger.info('update_status duration: %s' % (datetime.datetime.now() - a))
        # 更新上报状态
        Datasource.objects.get(cc_biz_id=cc_biz_id, id=ds_id).update_report_status()
        # logger.info('update_report_status duration: %s' % (datetime.datetime.now() - a))
        ds_qs = AgentStatus.objects.filter(
            ds_id=ds_id
        ).order_by('-create_time').values('ip', 'status', 'update_time')
        total = ds_qs.count()
        ds_list = Datasource.bulid_list_data(ds_qs, int(page), int(page_size))
        res = {
            'result': True,
            'message': '',
            'data': {'total': total, 'data_list': ds_list}
        }
    except Exception as e:
        res = {
            'result': False,
            'message': e.message,
            'data': ''
        }
    # logger.info('get_agent_status duration: %s' % (datetime.datetime.now() - a))
    return render_json(res)


@decorators.check_perm
def get_ds_data_total(request, cc_biz_id, ds_id):
    """
    获取数据源的数据明细总数

    :param request:
    :param cc_biz_id:
    :param ds_id:
    :return: dict
        {
            'result': True/False,
            'message': 'message',       # 提示信息
            'data': 100,                # 总数
        }
    """
    try:
        ds = Datasource.objects.get(id=ds_id, cc_biz_id=cc_biz_id)
        date = request.GET.get('date', '')
        res = ds.get_detail_data_total(date)
    except Exception as e:
        res = {
            'result': False,
            'message': e.message,
            'data': 0
        }
    return render_json(res)


@decorators.check_perm
def get_ds_data_list(request, cc_biz_id, ds_id, page, page_size):
    """
    获取数据源的数据明细

    :param request:
    :param cc_biz_id:
    :param ds_id:
    :param page: 当前页面
    :param page_size: 每页的条数
    :return: dict
        {
            'result': True/False,
            'message': 'message',       # 提示信息
            'data': {
                'total': 100,   # 总数
                'list': [],  # 当前页的列表数据
            }
        }
    """
    try:
        ds = Datasource.objects.get(id=ds_id, cc_biz_id=cc_biz_id)
        date = request.GET.get('date', '')
        res = ds.get_detail_data(date, page, page_size)
    except Exception as e:
        res = {
            'result': False,
            'message': e.message,
            'data': None
        }
    return render_json(res)


@decorators.check_perm
def config_ds(request, cc_biz_id, ds_id):
    """
    获取数据源的数据明细

    :param request:
    :param cc_biz_id:
    :param ds_id: 为0时表示新增
    :return:
    """
    if request.method == 'POST':
        try:
            ds_id = int(ds_id)
            ds_data = json.loads(request.POST['datasource_data'])
            # 获取采集对象ip列表
            ds_data['ips'] = get_unique_list(
                convert_textarea_to_list(ds_data['ips'])
            )
            # 去除空格
            ds_data = strip(ds_data)
            # 校验数据合法性
            Datasource.validate_ds_correct(ds_data)
            # 数据加工，ips、field里面增加额外数据
            Datasource.deco_ds_data(ds_data)
            with transaction.atomic():
                # 新增逻辑
                if ds_id == 0:
                    # 同业务下数据表名不能重复
                    if Datasource.objects.filter(
                            cc_biz_id=cc_biz_id,
                            data_set=ds_data['data_set']
                    ).exists():
                        raise Exception(
                            u"表名：%s 在其它数据源中已使用，"
                            u"请输入一个唯一的表名" % ds_data['data_set']
                        )
                    ds = Datasource.objects.create(
                        cc_biz_id=cc_biz_id,
                        data_set=ds_data['data_set'],
                        data_desc=ds_data['data_desc'],
                        data_json=json.dumps(ds_data),
                        status=DS_STATUS.CREATE,
                        creator=request.user.username,
                        update_user=request.user.username,
                        data_id='0'
                    )
                    # 生成ip状态记录
                    for ip in ds_data['ips']:
                        AgentStatus.objects.create(
                            ds_id=ds.id,
                            ip=ip,
                            status=DS_STATUS.CREATE,
                            creator=request.user.username
                        )

                # 更新逻辑
                else:
                    ds = Datasource.objects.get(id=ds_id, cc_biz_id=cc_biz_id)
                    # 校验数据源更新时，不可修改的字段
                    if not Datasource.validate_ds_immutable(
                            json.loads(ds.data_json), ds_data
                    ):
                        raise Exception(u"异常请求，请通过页面提交数据")
                    if ds.status != DS_STATUS.NORMAL:
                        raise Exception(u"当前数据源不可编辑")
                    ds.data_json = json.dumps(ds_data)
                    ds.status = DS_STATUS.CREATE
                    ds.update_user = request.user.username
                    ds.save()

                # 调用后台接口，下发数据源配置
                ds.sync_to_server()

                # 调用后台接口，下发IP配置
                ds.sync_ips(','.join(ds.get_ip_list()), 'on')

                # ip状态更新为接入中
                AgentStatus.objects.filter(ds_id=ds.id).update(status=DS_STATUS.CREATE)

            res = {
                'result': True,
                'message': 'ok',
                'data': None
            }
        except RequestsResultException as e:
            res = {
                'result': False,
                'message': e.message,
                'data': None
            }
        except Exception as e:
            res = {
                'result': False,
                'message': e.message,
                'data': None
            }
        return render_json(res)
    else:
        return render_mako_context(
            request,
            '/monitor/datasource/config.html',
            {'cc_biz_id': cc_biz_id}
        )


@decorators.check_perm
def toggle_ds(request, cc_biz_id, action, ds_id):
    """
    数据源启用、停用
    :param request:
    :param cc_biz_id:
    :param action:
    :param ds_id:
    :return:
    """
    try:
        ds = Datasource.objects.get(id=ds_id, cc_biz_id=cc_biz_id)
        if ((action == 'on' and ds.status == DS_STATUS.STOPPED) or
                (action == 'off' and ds.status == DS_STATUS.NORMAL)):
            ds.sync_ips(','.join(ds.get_ip_list()), action)
            ds.status = DS_STATUS.STOP if action == 'off' else DS_STATUS.CREATE
            ds.update_user = request.user.username
            ds.save()
            AgentStatus.objects.filter(ds_id=ds.id).update(status=ds.status)
        else:
            raise Exception(u"当前状态不可启用或停用")
        res = {
            'result': True,
            'message': '',
            'data': None
        }
    except Exception as e:
        res = {
            'result': False,
            'message': e.message,
            'data': None
        }
    return render_json(res)


@decorators.check_perm
def manage_agent(request, cc_biz_id, action, ds_id, ip):
    """
    新增/删除/重新下发agent
    :param request:
    :param cc_biz_id:
    :param action: append、remove、refresh
    :param ds_id:
    :param ip:
    :return:
    """
    ds = Datasource.objects.get(cc_biz_id=cc_biz_id, id=ds_id)
    res = {
        'result': True,
        'message': '',
        'data': None,
        'action': action,
    }
    try:
        # 校验状态
        if ds.status not in (DS_STATUS.CREATE, DS_STATUS.NORMAL):
            raise Exception(u"当前状态不可新增")
        with transaction.atomic():
            if action == 'append':
                AgentStatus.objects.create(
                    ds_id=ds_id, ip=ip, status=DS_STATUS.CREATE,
                    creator=request.user.username
                )
                sync_action = 'on'
            else:
                agent = AgentStatus.objects.get(ds_id=ds_id, ip=ip)
                # 校验状态
                if agent.status not in (DS_STATUS.NORMAL, DS_STATUS.EXCEPTION):
                    raise Exception(u"当前状态不可操作")
                agent.status = DS_STATUS.DELETE if action == 'remove' else DS_STATUS.CREATE
                agent.save()
                sync_action = 'off' if action == 'remove' else 'on'
            # 调用下发接口
            ds.sync_ips(ip, sync_action)
    except IntegrityError:
        res['result'] = False
        res['message'] = u'IP: %s已经存在，请不要重复添加.' % ip
    except Exception as e:
        res['result'] = False
        res['message'] = e.message
    return render_json(res)


@decorators.check_perm
def get_options(request, cc_biz_id):
    config_names = request.GET['config_name']
    config_name_list = config_names.split('|')
    data = {}
    for config_name in config_name_list:
        data[config_name] = Datasource.get_select_options(config_name)
    return render_json({'result': True, 'message': 'ok', 'data': data})


@decorators.check_perm
def get_ds_monitors(request, cc_biz_id, ds_id):
    """
    获取数据源关联监控项
    :param request:
    :param cc_biz_id:
    :param ds_id:
    :return:
    """
    try:
        ds = Datasource.objects.get(cc_biz_id=cc_biz_id, id=ds_id)
        res = ds.get_monitors()
    except RequestsResultException as e:
        res = {
            'result': False,
            'message': u"拉取关联监控项失败：%s" % e.message,
            'data': None
        }
    return render_json(res)


@decorators.check_perm
def update_ds_status(request, cc_biz_id):
    """
    更新数据源的状态
    :param request:
    :param cc_biz_id:
    :return:
    """
    for ds in Datasource.objects.filter(cc_biz_id=cc_biz_id):
        ds.update_status()
    return render_json()