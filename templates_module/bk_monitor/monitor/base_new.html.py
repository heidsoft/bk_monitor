# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1495878375.220013
_enable_loop = True
_template_filename = u'/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/base_new.html'
_template_uri = u'/monitor/base_new.html'
_source_encoding = 'utf-8'
_exports = [u'iframe_content', u'cssfile', u'scriptfile', u'script']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'/base.html', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def cssfile():
            return render_cssfile(context._locals(__M_locals))
        def script():
            return render_script(context._locals(__M_locals))
        APP_CODE = context.get('APP_CODE', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        def iframe_content():
            return render_iframe_content(context._locals(__M_locals))
        def scriptfile():
            return render_scriptfile(context._locals(__M_locals))
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'cssfile'):
            context['self'].cssfile(**pageargs)
        

        __M_writer(u'\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'iframe_content'):
            context['self'].iframe_content(**pageargs)
        

        __M_writer(u'\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'scriptfile'):
            context['self'].scriptfile(**pageargs)
        

        __M_writer(u'\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'script'):
            context['self'].script(**pageargs)
        

        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_iframe_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def iframe_content():
            return render_iframe_content(context)
        __M_writer = context.writer()
        __M_writer(u'\n\t<!--    iframe      -->\n    <div id="detailIframe" style="background-color: rgb(255, 255, 255);position:fixed;width:100%;height:100%;display:none;z-index: 1002;">\n<!--          <a class="king-btn king-primary fr mt10" title="\u8fd4\u56de" href="###" id="back_btn_id"  onclick="closeDetailIframe(iframeCallBack)">\n\t\t    <i class="fa fa-mail-reply-all btn-icon"></i>\u8fd4\u56de\n\t\t</a> -->\n\t\t<iframe frameborder="0" id="detail_frame" name="detail_frame" src="" style="width:100%;height:100%;overflow:auto;"></iframe>\n\t</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_cssfile(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def cssfile():
            return render_cssfile(context)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n    <!-- Bootstrap css -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/bootstrap-3.3.4/css/bootstrap.min.css" rel="stylesheet">\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/font-awesome/css/font-awesome.min.css" rel="stylesheet">\n    <!-- \u5f53\u524d\u9879\u76ee\u6837\u5f0f\u6587\u4ef6 -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'css/sb-admin.css" rel="stylesheet">\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'css/sb-bk-theme.css" rel="stylesheet">\n    <!--\u84dd\u9cb8\u63d0\u4f9b\u7684\u516c\u7528\u6837\u5f0f\u5e93 -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'css/bk.css" rel="stylesheet">\n    <!--\u524d\u7aef\u5f00\u53d1\u8005\u63d0\u4f9b\u7684\u6837\u5f0f -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'css/alert.css" rel="stylesheet">\n    <!--\u540e\u7aef\u5f00\u53d1\u8005\u63d0\u4f9b\u7684\u6837\u5f0f -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/artDialog-6.0.4/css/ui-dialog.css" rel="stylesheet">\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/select2-3.5.2/select2.css" rel="stylesheet">\n    <!-- \u5de6\u4fa7\u4e0b\u62c9\u641c\u7d22\u5bfc\u822a\u680f -->\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/jquery.sumoselect-2.0.0/sumoselect.css" rel="stylesheet">\n    <link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/mCustomScrollbar-3.0.9/jquery.mCustomScrollbar.css" rel="stylesheet">\n\n    <!-- \u5982\u679c\u8981\u4f7f\u7528Bootstrap\u7684js\u63d2\u4ef6\uff0c\u5fc5\u987b\u5148\u8c03\u5165jQuery -->\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'js/jquery-1.10.2.min.js"></script>\n    <!-- \u5305\u62ec\u6240\u6709bootstrap\u7684js\u63d2\u4ef6\u6216\u8005\u53ef\u4ee5\u6839\u636e\u9700\u8981\u4f7f\u7528\u7684js\u63d2\u4ef6\u8c03\u7528\u3000-->\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/bootstrap-3.3.4/js/bootstrap.min.js"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scriptfile(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        APP_CODE = context.get('APP_CODE', UNDEFINED)
        def scriptfile():
            return render_scriptfile(context)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n\t<!-- \u8fd9\u4e2a\u662f\u5168\u5c40\u914d\u7f6e\uff0c\u5982\u679c\u9700\u8981\u5728js\u4e2d\u4f7f\u7528app_code\u548csite_url,\u5219\u8fd9\u4e2ajavascript\u7247\u6bb5\u4e00\u5b9a\u8981\u4fdd\u7559 -->\n\t<script type="text/javascript">\n\t\tvar app_code = "')
        __M_writer(unicode(APP_CODE))
        __M_writer(u'";\t\t\t// \u5728\u84dd\u9cb8\u7cfb\u7edf\u91cc\u9762\u6ce8\u518c\u7684"\u5e94\u7528\u7f16\u7801"\n\t\tvar site_url = "')
        __M_writer(unicode(SITE_URL))
        __M_writer(u'";\t\t\t// app\u7684url\u524d\u7f00,\u5728ajax\u8c03\u7528\u7684\u65f6\u5019\uff0c\u5e94\u8be5\u52a0\u4e0a\u8be5\u524d\u7f00\n        var static_url = "')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'";\n        var cc_biz_id = "')
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'";\n        var page_load_count = 0;\n\t</script>\n\n    <!--\u914d\u7f6ejs  \u52ff\u5220-->\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'js/settings.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/topbar-1.0/topbar.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/select2-3.5.2/select2.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/artDialog-6.0.4/dist/dialog-min.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/jquery.sumoselect-2.0.0/jquery.sumoselect.min.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'js/vue.min.js"></script>\n    <script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'js/utils.js"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_script(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def script():
            return render_script(context)
        __M_writer = context.writer()
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"129": 34, "130": 37, "131": 37, "132": 38, "133": 38, "134": 39, "135": 39, "136": 40, "137": 40, "138": 45, "139": 45, "140": 46, "141": 46, "142": 47, "143": 47, "144": 48, "145": 48, "146": 49, "147": 49, "148": 50, "149": 50, "150": 51, "151": 51, "27": 0, "157": 53, "163": 53, "169": 163, "44": 1, "49": 24, "54": 33, "59": 52, "64": 54, "70": 25, "76": 25, "82": 2, "89": 2, "90": 4, "91": 4, "92": 5, "93": 5, "94": 7, "95": 7, "96": 8, "97": 8, "98": 10, "99": 10, "100": 12, "101": 12, "102": 14, "103": 14, "104": 15, "105": 15, "106": 17, "107": 17, "108": 18, "109": 18, "110": 21, "111": 21, "112": 23, "113": 23, "119": 34}, "uri": "/monitor/base_new.html", "filename": "/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/base_new.html"}
__M_END_METADATA
"""
