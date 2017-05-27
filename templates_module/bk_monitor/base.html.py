# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1495878375.263122
_enable_loop = True
_template_filename = u'/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/base.html'
_template_uri = u'/base.html'
_source_encoding = 'utf-8'
_exports = [u'iframe_content', u'cssfile', u'script', u'content', u'scriptfile', u'css']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        APP_PATH = context.get('APP_PATH', UNDEFINED)
        def cssfile():
            return render_cssfile(context._locals(__M_locals))
        def script():
            return render_script(context._locals(__M_locals))
        int = context.get('int', UNDEFINED)
        request = context.get('request', UNDEFINED)
        cc_biz_names = context.get('cc_biz_names', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        def iframe_content():
            return render_iframe_content(context._locals(__M_locals))
        BK_PAAS_HOST = context.get('BK_PAAS_HOST', UNDEFINED)
        def scriptfile():
            return render_scriptfile(context._locals(__M_locals))
        sorted = context.get('sorted', UNDEFINED)
        def content():
            return render_content(context._locals(__M_locals))
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        def css():
            return render_css(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer(u'<!DOCTYPE html>\n<html lang="en" style="height:100%;">\n<head>\n    <link rel="icon" href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/monitor.ico" type="image/x-icon" />\n    <link rel="shortcut icon" href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/monitor.ico" type="image/x-icon" />\n\t<meta charset="utf-8" />\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    ')

        common_prefix = '%s%s' % (SITE_URL, cc_biz_id)
        if APP_PATH.startswith(common_prefix + '/bp/'):
            app_title = u'主机监控'
        elif APP_PATH.startswith(common_prefix + '/operation_monitor/'):
            app_title = u'自定义监控'
        elif APP_PATH.startswith(common_prefix + '/config/'):
            app_title = u'监控配置'
        elif APP_PATH.startswith(common_prefix + '/event_center/'):
            app_title = u'事件中心'
        elif APP_PATH.startswith(common_prefix + '/datasource/'):
            app_title = u'数据源接入'
        else:
            app_title = u'首页'
            
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['app_title','common_prefix'] if __M_key in __M_locals_builtin_stored]))
        __M_writer(u'\n    <title>\u84dd\u9cb8\u76d1\u63a7|\u84dd\u9cb8\u667a\u4e91\u793e\u533a\u7248</title>\n    <style type="text/css">\n        .star-chart-panel{\n            min-height: initial !important;\n        }\n    </style>\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'cssfile'):
            context['self'].cssfile(**pageargs)
        

        __M_writer(u'\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'css'):
            context['self'].css(**pageargs)
        

        __M_writer(u'\n</head>\n<body class="sidebar-collapse" style="overflow-y:auto;position:relative;padding-bottom: 60px;height:auto;min-height:100%;margin-top:0;padding-top:50px;">\n<div class="alert-mask hidden"></div>\n    <div id="wrapper">\n        <!-- Navigation -->\n        <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">\n            <!-- Brand and toggle get grouped for better mobile display -->\n            <div class="navbar-header">\n                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">\n                    <span class="sr-only">Toggle navigation</span>\n                    <span class="icon-bar"></span>\n                    <span class="icon-bar"></span>\n                    <span class="icon-bar"></span>\n                </button>\n                <a class="navbar-brand" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(u'" style="padding-left: 0;">\n                    <img src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/newlogo.png" class="king-J-icon inline-block">\n                    <span class="logo-lg hidden-xs">Jungle Alert</span>\n                </a>\n            </div>\n            <ol class="breadcrumb" id="breadcrumb">\n                <!--\n                <li>\n                    <a href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(u'"><i class="fa fa-home fa-2"></i> \u9996\u9875</a>\n                </li>\n                <li id="append-bread-2" style="display:none">\n                    <a href="###" id="append-bread-2-a"> </a>\n                </li>\n                -->\n                <li class="active" id="append-bread-1" style=""></li>\n            </ol>\n            <!-- Top Menu Items -->\n            <ul class="nav navbar-right top-nav">\n                <li>\n                    <form class="navbar-form">\n                      <div class="sidebar-menu plugin3_demo" id="plugin3_demo2">\n                          <span class="hidden-xs">\u5f53\u524d\u4e1a\u52a1\uff1a</span>\n                          <!-- select2 \u901a\u8fc7javascript start -->\n                          <input type="text" class="select2_box form-control" style="width:230px;">\n                          <!-- select2 \u901a\u8fc7javascript end -->\n                      </div>\n                    </form>\n                </li>\n                <li>\n                    <a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown">\n                        <!-- <i class="fa fa-user"></i>  -->\n                        ')
        __M_writer(unicode(request.user.chname))
        __M_writer(u' <b class="caret hide"></b>\n                    </a>\n                </li>\n                <li class="dropdown hidden-xs">\n                    <a id="logout" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(u'account/logout/">\u6ce8\u9500</a>\n                </li>\n\n            </ul>\n            <!-- Sidebar Menu Items - These collapse to the responsive navigation menu on small screens -->\n            <div class="collapse navbar-collapse navbar-ex1-collapse">\n                <ul class="nav navbar-nav side-nav">\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/overview/"><i class="fa fa-dashboard"></i> <span class="sidebar-text">\u9996\u9875</span></a>\n                    </li>\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/bp/" data-toggle="collapse" data-target="#demo"><i class="fa fa-hdd-o"></i> <span class="sidebar-text">\u4e3b\u673a\u76d1\u63a7</span></a>\n                    </li>\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/operation_monitor/"><i class="fa fa-line-chart"></i> <span class="sidebar-text">\u81ea\u5b9a\u4e49\u76d1\u63a7</span></a>\n                    </li>\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/config/" data-toggle="collapse" data-target="#demo1"><i class="fa fa-cog"></i> <span class="sidebar-text">\u76d1\u63a7\u914d\u7f6e</span></a>\n                    </li>\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/datasource/"><i class="fa fa-database"></i> <span class="sidebar-text">\u6570\u636e\u6e90\u63a5\u5165</span></a>\n                    </li>\n                    <li>\n                        <a class="side-li" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/event_center/"><i class="fa fa-calendar"></i> <span class="sidebar-text">\u4e8b\u4ef6\u4e2d\u5fc3</span></a>\n                    </li>\n                </ul>\n            </div>\n            <!-- /.navbar-collapse -->\n        </nav>\n\n        <div id="page-wrapper">\n\n            <div class="container-fluid iframe-container">\n                <div>\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer(u'\n                </div>\n                <!-- /.row -->\n')
        __M_writer(u'\t\t\t\t<div class="iframe-div" style="display:none;">\n\t\t\t\t    <div class="p15">\n<!-- \t\t\t\t        <div class="iframe-back mb15 fr">\n\t\t\t\t            <button class="king-btn king-primary">\u8fd4\u56de</button>\n\t\t\t\t        </div> -->\n\t\t\t\t        <div id="iframe_body" style="overflow-y: auto;">\n\t\t\t\t        </div>\n\t\t\t\t    </div>\n\t\t\t\t</div>\n')
        __M_writer(u'\n            </div>\n            <!-- /.container-fluid -->\n        </div>\n        <!-- /#page-wrapper -->\n    </div>\n    <!-- /#wrapper -->\n    <!-- footer -->\n        <div class="footer-menu text-center" style="position: absolute;bottom: 0;width: 100%;padding-left: 50px;height: 60px;overflow: hidden;">\n            <p>\n                <a href="###" id="contact_us" class="link">QQ\u54a8\u8be2</a>\n                    <script src="//wp.qiye.qq.com/loader/4.0.0.js" charset="utf-8"></script>\n                    <script type="text/javascript">\n                       try{\n                          __WPA.create({\n                              nameAccount:"800802001",\n                              customEle: document.getElementById(\'contact_us\')\n                          })\n                       }catch(err){}\n                    </script>\n                | <a href="http://bbs.bk.tencent.com/forum.php" target="_blank" hotrep="hp.footer.feedback" class="link">\u84dd\u9cb8\u8bba\u575b</a>\n                | <a href="http://bk.tencent.com/" target="_blank" hotrep="hp.footer.feedback" class="link">\u84dd\u9cb8\u5b98\u7f51</a>\n                | <a href="')
        __M_writer(unicode(BK_PAAS_HOST))
        __M_writer(u'/platform/" target="_blank" hotrep="hp.footer.feedback" class="link">\u84dd\u9cb8\u667a\u4e91\u5de5\u4f5c\u53f0</a>\n            </p>\n            <p class="f12">Copyright \xa9 2012-2017 Tencent BlueKing. All Rights Reserved ( \u84dd\u9cb8\u667a\u4e91 \u7248\u6743\u6240\u6709 )</p>\n        </div>\n\n    <!-- /#wrapper -->\n')
        __M_writer(u'\t<script>\n\tfunction open_div(url, callback){\n\t\t$iframeW=$(\'.iframe-container\').width();\n\t\t$iframeH=$(window).height()-85;\n\t\t// TODO .iframe-div \u4e2d\u52a0\u8f7d \u914d\u7f6e\u9875\u9762\u5185\u5bb9\n\t\t$("#iframe_body").load(url, function(response,status,xhr){\n            $("#iframe_body").css({\n                \'height\': $iframeH\n            });\n        });\n\t\t$(\'.iframe-div\').css({\n            \'margin-top\': \'-15px\',\n\t\t    "width": $iframeW,\n            \'min-height\':$iframeH\n\t\t}).fadeIn(\'fast\', function() {\n')
        __M_writer(u'\t\t});\n\t\t$(window).resize(function(event) {\n\t\t    $iframeW=$(\'.iframe-container\').width();\n\t\t    $(\'.iframe-div\').css({\n\t\t        "width": $iframeW\n\t\t    });\n            $("#iframe_body").css({\n                \'height\': $(window).height()-85\n            });\n\t\t});\n        $(window).scrollTop(0);\n        $("body").css("overflow", "hidden");\n        $(window).resize();\n        $(\'.iframe-back\').click(function (){\n            $(".iframe-div").fadeOut(\'fast\',function (){\n                $(this).siblings().css(\'display\',\'block\');\n                $("body").css("overflow", "auto")\n            })\n        })\n\t}\n\tfunction close_div(callback){\n\t\t// .iframe-div \u4e2d\u6e05\u9664 \u5185\u5bb9\n        $("body").css("overflow", "auto")\n\t\t$("#iframe_body").html(\'\');\n\t\t$(\'.iframe-div\').fadeOut(\'fast\', function() {\n')
        __M_writer(u'\t\t    $(".iframe-div").siblings().css(\'display\',\'block\');\n\t\t    // \u8fd4\u56de\u540e\u7684\u56de\u8c03\u51fd\u6570\n\t\t    callback && callback();\n\t\t});\n\t}\n\t</script>\n')
        __M_writer(u'\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'iframe_content'):
            context['self'].iframe_content(**pageargs)
        

        __M_writer(u'\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'scriptfile'):
            context['self'].scriptfile(**pageargs)
        

        __M_writer(u'\n    <script>\n    $(function (){\n\n        // \u4e1a\u52a1\u9009\u62e9\u6846 BEGIN\n        var bkArr = [\n')
        for biz_id, biz_name in sorted(cc_biz_names.items(), key=lambda x:int(x[0])):
            __M_writer(u'            { id: ')
            __M_writer(unicode(biz_id))
            __M_writer(u", text: '")
            __M_writer(unicode(biz_name))
            __M_writer(u"' },\n")
        __M_writer(u'        ];\n        $("#plugin3_demo2 .select2_box").select2({ data: bkArr });\n        $("#plugin3_demo2 .select2_box").on(\'change\',function(e){\n            self.location=site_url+e.val+"/')
        __M_writer(unicode('/'.join(request.path.replace(SITE_URL, "/").split('/')[2:])))
        __M_writer(u'";\n        });\n        $("#plugin3_demo2 .select2_box").select2("val", "')
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'");\n        // \u4e1a\u52a1\u9009\u62e9\u6846 END\n    })\n    //\u6253\u5f00iframe\n\tfunction openDetailIframe(url){\n\t\tvar winWidth = $(window).width();\n\t\tvar winHeight = $(window).height();\n\t\tvar sidebarWidth = 70;\n\t\tvar iframeWidth = winWidth - sidebarWidth;\n\t\tvar iframeHeight = winHeight - 50;\n\n\t\tvar iframeBox = $(\'#detailIframe\');\n\t\tiframeBox.css({left: sidebarWidth + \'px\',width: iframeWidth + \'px\', height: iframeHeight+\'px\'});\n\t\tiframeBox.find(\'iframe\').attr(\'src\', url).load(function(){\n\t\t\tdialog({id: \'show_tip\'}).close();\n\t\t\t$(\'#detailIframe\').animate({\n\t\t\t\t\'top\' : 50,\n\t\t\t\t\'opacity\' : \'show\'\n\t\t\t}, "fast");\n\t\t});\n\n\t};\n\t//\u5173\u95ediframe\n\tfunction closeDetailIframe (callback){\n\t\t$(\'#detailIframe\').animate({\n\t\t\t\'top\' : \'-100px\',\n\t\t\t\'opacity\' : \'hide\'\n\t\t}, "fast", function(){\n\t\t\tdialog({id: \'show_tip\'}).close();\n\t\t\tcallback && callback();\n\t\t});\n\t};\n    function alert_topbar(text, type, timeout){\n        // \u9876\u5c42tip\u5f39\u6846\u901a\u77e5\n        // text \u5185\u5bb9\n        // type \u7c7b\u578b\n        // \u81ea\u52a8\u6d88\u5931\u65f6\u95f4\uff0c\u5355\u4f4d\u6beb\u79d2\n        var topBarTimline = 0;\n        show_bar = function(options) {\n            $div = $("<div class=\'magic-topbar-container\' style=\'display:none;\'></div>");\n            if ((typeof options == \'object\') && options.constructor == Object) {\n                // \u8bbe\u7f6e\u9ed8\u8ba4\u503c\n                var defaults = {\n                        setClass: \'bg-primary\',\n                        close: function() {},\n                        timeOut: 0\n                    };\n                    // \u4f20\u53c2\u8bbe\u7f6e\n                options = $.extend(defaults, options);\n\n                // \u5224\u65ad\u9875\u9762\u662f\u5426\u6709\u63d0\u793a\u6761\n                if ($(\'.magic-topbar-container\').length>0) {\n                    $(\'.magic-topbar-container\').remove();\n                    clearTimeout(topBarTimline);\n                }\n                if ($(\'.\' + options.setClass).length == 0 ) {\n                    // \u751f\u6210\u63d0\u793a\u6761\n                    $div.addClass(options.setClass).appendTo(\'body\').html(\'<span>\' + options.text + \'</span>\');\n                    // \u6dfb\u52a0\u5173\u95ed\u6309\u94ae\n                    $div.append(\'<div class="magic-topbar-close" style="font-size:20px; float:right;margin:-5px -15px 0 0;cursor:pointer;">&times;</div>\');\n                    // \u963b\u6b62\u5192\u6ce1\u548c\u9ed8\u8ba4\u884c\u4e3a\n                    $div.on(\'click\', function() {\n                        return false;\n                    });\n                    // \u62c9\u51fa\u63d0\u793a\u6761\n                    $div.slideDown(500);\n                    // \u5173\u95ed\u6309\u94ae\u4e8b\u4ef6\n                    $(\'.magic-topbar-close\').on(\'click\', function() {\n                        var topbar = $(this).parent();\n                        topbar.slideUp(500, function(){\n                            topbar.remove();\n                        });\n                        options.close();\n                        return false;\n                    });\n                    // \u8bbe\u7f6e\u9ed8\u8ba4\u5173\u95ed\u65f6\u95f4\n                    function closeFn() {\n                        $(\'.magic-topbar-close\').trigger(\'click\');\n                        clearTimeout(topBarTimline);\n                    }\n                    if (!options.timeOut == 0 && options.timeOut > 0) {\n                        topBarTimline = setTimeout(closeFn, options.timeOut);\n                    }\n                    // \u9f20\u6807\u79fb\u5165\u79fb\u51fa\n                    $div.mouseenter(function() {\n                        clearTimeout(topBarTimline);\n                    });\n                    $div.mouseleave(function() {\n                        if (!options.timeOut == 0 && options.timeOut > 0) {\n                            topBarTimline = setTimeout(closeFn, options.timeOut);\n                        }\n                    })\n                }\n            }\n        };\n        var bar_class = "bg-info";\n        switch (type){\n            case "success":\n            case "ok":\n                bar_class = "bg-success";\n                break;\n            case "error":\n            case "fail":\n            case "danger":\n                bar_class = "bg-danger";\n                break;\n        }\n        show_bar({\n             text: text,\n             setClass:bar_class,\n             timeOut:timeout?timeout:1500,\n             close:function (){\n             }\n         });\n    }\n    function _app_confirm(msg, callback1, callback2) {\n        var d = dialog({\n            width: 260,\n            title: \'\u786e\u8ba4\',\n            content: msg,\n            okValue: \'\u786e\u5b9a\',\n            ok: function() {callback1()},\n            cancelValue: \'\u53d6\u6d88\',\n            cancel: function() {callback2()}\n        })\n        d.show();\n       return d;\n    }\n    function app_confirm(msg, callback) {\n        var d = dialog({\n            width: 260,\n            title: \'\u786e\u8ba4\',\n            content: msg,\n            okValue: \'\u786e\u5b9a\',\n            ok: function() {callback()},\n            cancelValue: \'\u53d6\u6d88\',\n            cancel: function() {}\n        })\n        d.show();\n       return d;\n    }\n    function app_alert(msg, type) {\n        var d = dialog({\n            width: 260,\n            title: \'\u6e29\u99a8\u63d0\u793a\',\n            cancel: function (){},\n            ok: function() {},\n            okValue: \'\u786e\u5b9a\',\n            cancel: false,\n            content: \'<div class="king-notice-box king-notice-\'+type+\'"><p class="king-notice-text">\'+msg+\'</p></div>\'\n        })\n        d.show();\n        return d;\n    }\n    function app_tip(msg, type) {\n        var d = dialog({\n            width: 260,\n            title: \'\u6e29\u99a8\u63d0\u793a\',\n            content: \'<div class="king-notice-box king-notice-\'+type+\'"><p class="king-notice-text">\'+msg+\'</p></div>\'\n        })\n        d.show();\n        return d;\n    }\n    function setCookie(c_name,value,expiredays)\n    {\n        var exdate=new Date()\n            exdate.setDate(exdate.getDate()+expiredays)\n            document.cookie=c_name+ "=" +escape(value)+\n            ((expiredays==null) ? "" : ";path=/;expires="+exdate.toGMTString())\n    }\n    function getCookie(c_name)\n    {\n        if (document.cookie.length>0)\n        {\n            c_start=document.cookie.indexOf(c_name + "=")\n                if (c_start!=-1)\n                {\n                    c_start=c_start + c_name.length+1\n                        c_end=document.cookie.indexOf(";",c_start)\n                        if (c_end==-1) c_end=document.cookie.length\n                            return unescape(document.cookie.substring(c_start,c_end))\n                }\n        }\n        return ""\n    }\n    setCookie("cc_biz_id", "')
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'", 60);\n    $(".side-li").each(function(i, value){\n        if ("')
        __M_writer(unicode(request.path))
        __M_writer(u'".indexOf($(value).attr("href"))!=-1){\n            $(value).parent().addClass("active");\n            $("#append-bread-1").html($(value).children(".sidebar-text").html());\n        }\n    })\n\n    /* \u8868\u5355\u6309\u56de\u8f66\u952e \u89e6\u53d1\u76f8\u5e94\u67e5\u8be2\u6309\u94ae\n     * input\u8868\u5355\u6dfb\u52a0 enter-to=\'id\' \u6307\u5411 \u67e5\u8be2\u6309\u94ae\u7684id\n     */\n    $(\'[enter-to]\').keydown({},function (event){\n        switch(event.keyCode){\n            case 13:\n            var _id=$(this).attr(\'enter-to\');\n            var searchBtn = $(\'#\'+_id);\n            if(searchBtn.length>0){\n               searchBtn.trigger(\'click\');\n            }\n            break;\n        }\n    })\n    </script>\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'script'):
            context['self'].script(**pageargs)
        

        __M_writer(u'\n</body>\n\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_iframe_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def iframe_content():
            return render_iframe_content(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_cssfile(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def cssfile():
            return render_cssfile(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_script(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def script():
            return render_script(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        __M_writer(u'\n                    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_scriptfile(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def scriptfile():
            return render_scriptfile(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_css(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def css():
            return render_css(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"128": 218, "129": 218, "130": 218, "131": 218, "132": 218, "133": 220, "134": 223, "135": 223, "136": 225, "137": 225, "138": 410, "139": 410, "140": 412, "141": 412, "16": 0, "146": 433, "174": 433, "152": 210, "208": 31, "163": 30, "42": 1, "43": 4, "44": 4, "45": 5, "46": 5, "47": 9, "219": 208, "185": 115, "191": 115, "65": 23, "197": 211, "70": 30, "75": 31, "76": 46, "77": 46, "78": 47, "79": 47, "80": 54, "81": 54, "82": 77, "83": 77, "84": 81, "85": 81, "86": 89, "87": 89, "88": 89, "89": 92, "90": 92, "91": 92, "92": 95, "93": 95, "94": 95, "95": 98, "96": 98, "97": 98, "98": 101, "99": 101, "100": 101, "101": 104, "102": 104, "103": 104, "108": 116, "109": 120, "110": 130, "111": 152, "112": 152, "113": 159, "114": 176, "115": 202, "116": 209, "121": 210, "126": 211, "127": 217}, "uri": "/base.html", "filename": "/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/base.html"}
__M_END_METADATA
"""
