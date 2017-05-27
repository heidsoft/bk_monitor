# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1495878377.808669
_enable_loop = True
_template_filename = '/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/overview/star_chart_panel.html'
_template_uri = '/monitor/overview/star_chart_panel.html'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        total_pages = context.get('total_pages', UNDEFINED)
        len = context.get('len', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        filter_loctaions = context.get('filter_loctaions', UNDEFINED)
        num_per_page = context.get('num_per_page', UNDEFINED)
        star_menu = context.get('star_menu', UNDEFINED)
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'                    <div class="row" style="overflow:auto;">\n')
        for l in filter_loctaions:
            __M_writer(u'\t                    <div class="col-xs-4 chart-one" data-monitor_backend_id="')
            __M_writer(unicode(l.monitor.backend_id))
            __M_writer(u'" data-monitor_id="')
            __M_writer(unicode(l.monitor.id))
            __M_writer(u'" data-system_menu="')
            __M_writer(unicode(l.menu.system_menu))
            __M_writer(u'" data-location_id="')
            __M_writer(unicode(l.id))
            __M_writer(u'" data-enabled="')
            __M_writer(unicode(1 if l.monitor.is_enabled else 0))
            __M_writer(u'">\n\t                        <div class="panel panel-default">\n\t                        <div class="panel-heading panel-heading-fix portlet-header">\n\t                            <span class="chart-title" title="')
            __M_writer(unicode(l.monitor.monitor_name))
            __M_writer(u'">')
            __M_writer(unicode(l.monitor.monitor_name))
            __M_writer(u'</span>\n\t                            <div class="pull-right warning-level">\n\t                                <label class="label event-danger mr5" title="\u4e25\u91cd\u544a\u8b66\uff0c\u70b9\u51fb\u67e5\u770b\u544a\u8b66\u5217\u8868">0</label>\n\t                                <label class="label event-warning mr5" title="\u666e\u901a\u544a\u8b66\uff0c\u70b9\u51fb\u67e5\u770b\u544a\u8b66\u5217\u8868">0</label>\n\t                                <label class="label event-info mr5" title="\u8f7b\u5fae\u544a\u8b66\uff0c\u70b9\u51fb\u67e5\u770b\u544a\u8b66\u5217\u8868">0</label>\n')
            __M_writer(u'                                    <button type="button" title="')
            __M_writer(unicode(u"取消关注" if l.monitor.favorite else u"关注"))
            __M_writer(u'" class="favorite ')
            __M_writer(unicode("active" if l.monitor.favorite else ""))
            __M_writer(u'" style="background-color: #FAFAFA;border: none;">\n                                        <i class="fa fa-star"></i>\n                                    </button>\n')
            __M_writer(u'\t                            </div>\n\t                        </div>\n\t                        <div class="charts-line-panel" style="height:250px;padding:10px;"></div>\n\t                        </div>\n\t                    </div>\n')
        if len(filter_loctaions) < num_per_page:
            __M_writer(u'\t                    <div class="col-xs-4 chart-one-add">\n\t                        <div class="panel panel-default">\n                                <div class="panel-heading panel-heading-fix portlet-header" style="text-align: center">\n                                <span class="chart-title" title="\u65b0\u589e\u5173\u6ce8">\u65b0\u589e\u5173\u6ce8</span>\n                                </div>\n\n                                <div class="chart-add" style="height:250px;padding:10px;text-align:center;">\n                                    <a data-toggle="modal" class="dialog-popup" href="')
            __M_writer(unicode(SITE_URL))
            __M_writer(unicode(cc_biz_id))
            __M_writer(u'/operation/monitor/location/add/?menu_id=')
            __M_writer(unicode(star_menu.id))
            __M_writer(u'&overview=1"><i class="fa fa-plus"></i></a>\n                                </div>\n\n\t                        </div>\n\t                    </div>\n')
        __M_writer(u'\t                </div>\n                    <script>\n                    total_star_graphs_pages = ')
        __M_writer(unicode(total_pages))
        __M_writer(u';\n                    menu_id = ')
        __M_writer(unicode(star_menu.id))
        __M_writer(u';\n                    </script>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"16": 0, "28": 1, "29": 2, "30": 3, "31": 3, "32": 3, "33": 3, "34": 3, "35": 3, "36": 3, "37": 3, "38": 3, "39": 3, "40": 3, "41": 6, "42": 6, "43": 6, "44": 6, "45": 12, "46": 12, "47": 12, "48": 12, "49": 12, "50": 16, "51": 22, "52": 23, "53": 30, "54": 30, "55": 30, "56": 30, "57": 30, "58": 36, "59": 38, "60": 38, "61": 39, "62": 39, "68": 62}, "uri": "/monitor/overview/star_chart_panel.html", "filename": "/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/overview/star_chart_panel.html"}
__M_END_METADATA
"""
