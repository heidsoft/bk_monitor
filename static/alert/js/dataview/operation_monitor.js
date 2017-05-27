$err_div = '<div class="p20 pt40" style="height:100%;">'+
    '<div class="alert alert-warning" role="alert" style="height:100%;max-height: 280px;overflow:auto;">'+
      '<p id="error_title" class="mb10"><b></b></p>'+
      '<p id="error_msg">SQL查询失败：原因：结果表 112_ja_online 不存在</p>'+
      '<p></p>'+
    '</div>'+
'</div>';

$shadow = '<div style="position: absolute;text-align: center;padding-top: 110px;z-index: 2;margin-left: -10px;margin-top: 26px;width: 100%;height: 250px;background-color: rgba(38,50,56,0.5);font-size: 20px;color: #020202;font-weight: 800;"><a href="###" style="color: #f5f5f5;">监控被禁用，点击启用</a></div>'

// Date.now 获取当前时间戳 million second
if (!Date.now) {
    Date.now = function() { return new Date().getTime(); }
}

// 回调代码: 1, 修改配置；2, 新增自定义监控 3， 场景接入
var callback_code
var menu_loading_icon;
var edit_menu_id = "";
// render left menu bar
Highcharts.setOptions(Highcharts.theme_default);

var g_notice = {
    show_msg: function(type, msg){
        app_alert(msg, type==="error"?"fail":"");
    }
};

function setRightHeight(){
    var H=$(window).height();
    // 左边列表高度设置
    $('.menu-list-ul').height(H-145);
    $('.menu-list-ul').mCustomScrollbar({
        theme: "minimal-dark",
        scrollSpeed:200
    });

    // $('#layoutLeft').css('height', (H-85));
    $('.charts-container').css("min-height", (H-187));

    $(window).scroll(function (e){
        $('.operation-content .layout-left').css("top",$(window).scrollTop());
    })
}

function render_left_menu(){
    function bind_menu_click(){
        $(".scene-list>li").off("click").on('click', function(e){
            if ($(e.target).is("i")){
                return
            }
            var a_selector = $(e.target).is("a")?$(e.target):$(e.target).find("a");
            menu_id = a_selector.attr("data-menu_id");
            if (!menu_id){return}
            $(".scene-list>li").removeClass("active");
            a_selector.parent().addClass("active");

            // 渲染右侧监控面板
            $("#right_panel").html("");
            $.get(site_url+cc_biz_id+'/'+"operation/monitor/graph/panel/", {menu_id: menu_id}, function(res){
                $(".loading-box").hide();
                $("#right_panel").html(res);
                bind_panel_event();
                make_graphs();
                //$("html,body").animate({scrollTop: 0}, 1000);
            });
            $(".loading-box").show();

        });
    }
    function init_left_menu(){
        menu_loading_icon = $("#menu_loading").hide();
        $ul.on('mouseenter', 'li', function(event){
            $(event.target).closest("li").removeClass('hover');
            $(this).addClass('hover');
        }).on('mouseleave', 'li', function(event){
            $(event.target).closest("li").removeClass('hover');
        });

        var leftBox = $('#layoutLeft');
        // 点击编辑按钮
        leftBox.on('click', '.fa-edit', function() {
            if($('.editing').length>0){
               $('.editing').find('.fa-close').trigger('click');
            }
            $(this).closest('li').addClass('editing');
            var $a = $(this).parent().siblings('a');
            var $aStr = $a.text();
            edit_menu_id = $a.attr("data-menu_id");
            $a.next('input').val($aStr).attr('data-text', $aStr).focus();
            return false;
        });

        // 点击确定
        leftBox.on('click', '.fa-check', function(event) {
            var $input = $(this).parent().siblings('input');
            var url = edit_menu_id==""?(site_url+cc_biz_id+'/'+"operation/monitor/menu/add/"):(site_url+cc_biz_id+'/'+"operation/monitor/menu/edit/");
            var $a = $(this).parent().siblings('a');
            var inputVal = $input.val();
            var $oLi=$(this).closest('li');
            if (inputVal == '') {
                //$input.tooltip('show');
                return false;
            }
            menu_loading_icon.show();
            $.post(url, {menu_id: edit_menu_id, menu_name:inputVal.trim()}, function(res){
                menu_loading_icon.hide();
                if (res.result){
                    //$input.tooltip('destroy');
                    $a.text(inputVal);
                    $a.attr("data-menu_id", res.data);
                    if ($oLi.hasClass('adding')) {
                        $oLi.appendTo($ul);
                    }
                    $oLi.removeClass('editing').removeClass('adding');
                    bind_menu_click();
                    $oLi.click();
                    alert_topbar("操作成功", "ok");
                }else{
                    $('.scene-section').find('.editing').find('.fa-close').trigger('click');
                    g_notice.show_msg('error', res.msg);
                }
            }, "json");
        });

        // 点击取消按钮
        leftBox.on('click', '.fa-close', function(event) {
            var $input = $(this).parent().siblings('input');
            var $a = $(this).parent().siblings('a');
            var $aText = $a.text();
            var $thisLi = $(this).closest('li');

            if ($thisLi.hasClass('editing')) {
                $input.val($aText);
                $thisLi.removeClass('editing');
            } else {
                app_confirm("确认删除分组？", function(){
                    // post delete request
                    menu_loading_icon.show();
                    var menu_id = $(event.target).closest('li').find('a').attr("data-menu_id");
                    $.post(site_url+cc_biz_id+'/'+"operation/monitor/menu/del/", {menu_id:menu_id}, function(res){
                        menu_loading_icon.hide();
                        if (res.result){
                            alert_topbar("删除成功", "ok");
                            if ($(event.target).closest("li").hasClass("active")){
                                $(event.target).closest("ul").find("li").first().click();
                            }
                            $(event.target).closest('li').remove();
                        }else{
                            g_notice.show_msg('error', res.msg);
                        }
                    }, 'json');
                });
            }
        });
        // 点击增加场景
        leftBox.on('click', '.add-one', function(event) {
            leftBox.find('.editing').find('.fa-close').trigger('click');
            edit_menu_id = "";
            var $newLi = $('<li class="editing adding">' +
                '<a class="text-over" href="javascript:;"></a>' +
                '<input type="text" class="form-control" data-text="" data-placement="bottom" value="" data-toggle="tooltip" title="">' +
                '<span class="edit-icon">' +
                '<i class="fa fa-edit ml5"></i> ' +
                '<i class="fa fa-check ml5"></i> ' +
                '<i class="fa fa-close ml5"></i> ' +
                '</span>' +
                '</li>');
            $newLi.prependTo($ul).find('input').focus();
        });

        leftBox.on('click', '.adding .fa-close', function(event) {
            $('.adding').remove();
        });

        // 点击其他区域取消操作
        $(document).on('click', function(event) {
            var sceneTarget = $(event.target).closest('.scene-section');
            if (!sceneTarget.length > 0) {
                $('.scene-section').find('.editing').find('.fa-close').trigger('click');
            }
        });
    }
    $.get(site_url+cc_biz_id+'/'+"operation/monitor/menu/list/", {}, function(res){
        $("#left_menu").html(res);
        $ul = $(".scene-list");
        init_left_menu();
        bind_menu_click();
        if (default_menu_id==""){
            $ul.find("li").first().click();
        }else{
            var default_li = $ul.find("a[data-menu_id="+ default_menu_id +"]");
            default_li?default_li.click():$ul.find("li").first().click();
        }
    });
    setRightHeight();
    $(window).resize(function (){ setRightHeight() });
    $("#add_custom").unbind("click").on("click", function(e){
        callback_code = 2;
        open_div(site_url+cc_biz_id+'/'+'config/custom/0/');
        //openDetailIframe(site_url+cc_biz_id+'/'+'config/custom/0/');
    });
    $("#add_keyword").unbind("click").on("click", function(e){
        callback_code = 2;
        open_div(site_url+cc_biz_id+'/'+'config/keyword/0/');
        //openDetailIframe(site_url+cc_biz_id+'/'+'config/custom/0/');
    });
}

var time_start = '00:00';
var time_end = '23:59';

function init_top_time_bar(){
//时间变化事件
    $(".timeline").selectable({
        stop: function() {
            var min = 24;
            var max = 0;
            $(".ui-selected", this).each(function() {
                var _this = $(this);
                    //var _val  = _this.attr("value")
                var _val = Number(_this.attr("value"));
                if (_val < min) {
                    min = _val
                }
                if (_val > max) {
                    max = _val
                }
            });
            if (min < 10) {
                min = "0" + min
            }
            if (max < 10) {
                max = "0" + max
            }
            time_start = min + ":00";
            time_end = max + ":59";
            if (!$(event.target).hasClass("icon-time")){
                make_graphs();
            }
        }
    });

    // 选择单个日期
    $('#daterangepicker').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: '提交',
            cancelLabel: '取消',
            fromLabel: '从',
            toLabel: '到',
            weekLabel: '周',
            customRangeLabel: '自定义范围',
            daysOfWeek: ['日', '一', '二', '三', '四', '五','六'],
            monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
            firstDay: 1
        },
        maxDate: moment(),
        autoApply: true,
        singleDatePicker: true,
        timePicker: false
    }).on("change", function(res){
        make_graphs();
    });
    //全选时间
    $(".icon-time").unbind("click").bind("click", function() {
        if ($(".timeblock.ui-selected").length != 24) {
            $(".timeblock").addClass('ui-selected');
            time_start = "00:00";
            time_end = "23:59";
        }
        make_graphs();
    });
}

function make_time_range(){
    // 获取当前时间范围
    var date = $("#daterangepicker").val();
    return date + ' ' + time_start + " -- " + date + " " + time_end
}

function make_graphs(){
    var contains = $(".chart-contain");
    for (var i=0;i<contains.length;i++){
        make_contain_graph($(contains[i]))
    }

}

function make_contain_graph(contain){
    var params = contain.find("div.chart-filter>form").serializeObject();
    params["time_range"] = make_time_range();
    var graph_panel = contain.find("div.king-block-content-chart");
    var monitor_id = contain.attr("data-monitor_id");
    if (!monitor_id){
        return
    }
    params["monitor_id"] = monitor_id;
    //contain.find(".loading").show();
    show_loading(contain);
    ready_info[monitor_id] = false;
    $.get(site_url+cc_biz_id+'/'+'operation/monitor/graph/point/', params, function(res){
        hide_loading(contain);
        if(res.result){
            Hchart.make_graph(res.data.data, graph_panel[0], monitor_id);
            //var chart_obj = graph_panel.highcharts();
            //if (chart_obj){
            //    chart_obj.credits.attr("加载耗时:" + res.data.spend_time + " 秒");
            //}
            //加载完图表后再加载告警事件，显示在图表上。1秒动画
                get_alerts_info(contain);

        }else{
            graph_panel.html("");
            var err_div = $($err_div).appendTo(graph_panel);
            //err_div.find("#error_msg").text(res.message).next().text(res.data.echo_sql!==""?("SQL: " + res.data.echo_sql): "");
            err_div.find("#error_msg").text(res.message);
            err_div.find("#error_title").text("");
            err_div.find("#error_msg").css({"text-align": "center","margin-top": "50px"});
        }
    }, 'json');
    if (contain.attr("data-enabled") == "0"){
        after_disabled_graph(contain)
    }
}

function after_disabled_graph(contain){
    add_shadow(contain);
    // 禁用图标上的刷新和条件过滤按钮
    contain.find(".refresh").unbind("click").css("cursor", "not-allowed").attr("title", "启用监控后，刷新功能将可用");
    contain.find(".chart-filter-btn").unbind("click").css("cursor", "not-allowed").attr("title", "启用监控后，过滤功能将可用");
    contain.find(".m_disabled").closest("li").hide();
}


function open_graph_detail($this){
    if ($this.attr("disabled")){
        return
    }
    // 加载 graph detail 弹层 new in 2016/11/04
    $this.attr("disabled", true);
    var contain = $this.closest(".chart-contain");
    var monitor_id = contain.attr("data-monitor_id");
    var value_method = contain.find("select[name=value_method]").val();
    $.get(site_url+cc_biz_id+"/operation/monitor/graph_detail/", {monitor_id:monitor_id, value_method:value_method}, function(res){
        $this.attr("disabled", false);
        $(".monitor-popup").removeClass("hidden").html(res);
        $('.alert-mask').removeClass('hidden');
    });
}



function bind_panel_event(){
    $(".graph_detail").unbind("click").on("click", function(e){
        open_graph_detail($(e.target));
    });
    $("#refresh_all").unbind("click").on("click", function(e){
        make_graphs();
    });
    setRightHeight();
    $("button.chart-filter-btn").unbind().on("click", function(e){
        $(e.target).closest("button").toggleClass("expand");
        $(e.target).closest(".king-block-header").next().slideToggle("fast");
    });
    var web_filter = $(".web-filter");
    for (var i=0; i<web_filter.length; i++){
        init_web_filter_selector($(web_filter[i]), "")
    }
    // 刷新
    $("button.refresh").unbind('click').on('click', function(e){
        var contain = $(e.target).closest(".chart-contain");
        make_contain_graph(contain);
    });
    // 配置
    $("button.settings").unbind('click').on('click', function(e){
        callback_code = 1;
        var url = $(e.target).closest("button").attr("data-url");
        open_div(url);
        //openDetailIframe(url);
    });
    // 禁用
    $("button.m_disabled").unbind('click').on('click', function(e){
        var contain = $(e.target).closest(".chart-contain");
        var monitor_id = contain.attr("data-monitor_id");
        app_confirm("是否确认停用？", function(){
            $.post(site_url+cc_biz_id+"/config/operate_monitor/"+monitor_id+ '/', {is_enabled:0}, function(res){
                if (res.result){
                    alert_topbar("监控禁用成功", "ok");
                    after_disabled_graph(contain);
                }else{
                    app_alert(res.message, "fail");
                }
            }, 'json');
        });
    });

    $("select[name=value_method]").unbind("change").on("change", function(e){
        var contain = $(e.target).closest(".chart-contain");
        contain.find(".value-method").text($(e.target).find("option:selected").text());
        make_contain_graph(contain);
    });

    $(".chart-filter").find("input").unbind("change").on("change", function(e){
        var contain = $(e.target).closest(".chart-contain");
        // init_web_filter_selector
        // 根据目前的filter刷新新的数据
        var ext_filter = contain.find("div.chart-filter>form").serializeObject();
        delete ext_filter["value_method"];
        var web_filter = contain.find(".web-filter");
        for (var i=0; i<web_filter.length; i++){
            var field = $(web_filter[i]).find("input").last().attr("name");
            if (!ext_filter[field]){
                $(web_filter[i]).removeClass("inited");
                init_web_filter_selector($(web_filter[i]), ext_filter);
            }

        }
        make_contain_graph(contain);
    });

    // 收藏/取消收藏
    $("button.favorite").unbind("hover").hover(function(e){
        var a_dom = $(e.target).closest("button");
        if (!a_dom.hasClass("active")){
            a_dom.addClass("hover");
        }
    }, function(e){
        var a_dom = $(e.target).closest("button");
            a_dom.removeClass("hover");
    }).unbind("click").on("click", function(e){
        var a_dom = $(e.target).closest("button");
        var monitor_id = $(e.target).closest(".chart-contain").attr("data-monitor_id");
        $.post(site_url+cc_biz_id+'/'+"operation/monitor/favorite/toggle/", {monitor_id:monitor_id}, function(res){
            if (res.result){
                if (res.data.status){
                    alert_topbar("关注成功", "ok");
                    a_dom.addClass("active").attr("title", "取消关注");
                }else{
                    alert_topbar("取消关注成功", "ok");
                    a_dom.removeClass("active").attr("title", "关注");
                    // 在收藏夹菜单点击取消收藏的，等于删除
                    if ($(e.target).closest(".chart-contain").attr("data-system_menu")==="favorite"){
                        $(e.target).closest(".chart-contain").remove();
                    }
                }
            }else{
                app_alert(res.message, "fail");
            }
        }, "json");
    });

    $("button.delete").off("click").on("click", function(e){
        var contain = $(e.target).closest(".chart-contain");
        var monitor_id = contain.attr("data-monitor_id");
        var notice;
        if (contain.attr("data-delete_able") == 1){
            notice = '<div id="user_guider">' +
                '<div class="pb10 pt10 text-center">' +
                '   是否确认移除该视图？' +
                '</div>' +
                '<div class="text-center">' +
                '    <label class="checkbox-inline text-left">' +
                '         <span style="color:red"><input name="del_monitor" type="checkbox" value="1">同时删除该监控项</span>' +
                '      </label>' +
                '   </div>' +
                '</div>';
        }else{
            notice = '<div id="user_guider">' +
                '<div class="pb10 pt10 text-center">' +
                '   是否确认移除该视图？' +
                '</div>' +
                '<div class="text-center">' +
                '    <label class="checkbox-inline text-left">' +
                '         <span style="color:red;cursor: not-allowed;"><input name="del_monitor" type="checkbox" value="1" disabled>同时删除该监控项</span>' +
                '      </label>' +
                '   </div>' +
                '</div>';
        }
        var d = dialog({
            width: 260,
            title: '操作确认',
            content: notice,
            okValue: '确定',
            ok: function(e){
                var params = {location_id: contain.attr("data-location_id")};
                if ($("input[name=del_monitor]").prop("checked")){
                    params["del_monitor"] = "1";
                }
                $.post(site_url+cc_biz_id+'/'+"operation/monitor/location/del/", params, function(res){
                    if (res.result){
                        alert_topbar("删除成功", "ok");
                        contain.remove();
                        d.close().remove();
                    }else{
                        app_alert("删除失败", "fail");
                    }
                }, 'json');
                return true
            },
            cancelValue: '取消',
            cancel: function() {}
        }).show();
    });
    $("a.scenario").unbind("click").on("click", function(e){
        var url = $(e.target).attr("data-url");
        callback_code = 3;
        open_div(url);
        //openDetailIframe(url);
    });
    $("a.dialog-popup").unbind("click").on('click', function () {
        var that = $(this);
        var modal_handle = $('#modal');
        var modal_url = that.attr('href');
        var callback = that.attr('callback') || "";

        modal_handle.load(modal_url, function (responseTxt, statusTxt, xhr) {
            if (statusTxt == "success") {
                if (responseTxt.substr(0, 1) == '{' && responseTxt.substr(-1, 1) == '}') {
                    var test = eval('(' + responseTxt + ')');
                    if (test && test.message) {
                        alert(test.message);
                        return;
                    }
                }

                modal_handle.modal({
                  keyboard: false,
                  backdrop: 'static'
                });

                if (callback != "") {
                    eval(callback + "()");
                }
            }
            if (statusTxt == "error") {
                alert("打开失败 " + xhr.status + ": " + xhr.statusText);
            }
        });
        return false;
    });
    // 禁用的监控样式
    var disabled_monitors = $(".charts-container").find(".chart-contain[data-enabled=0]");
    disabled_monitors.each(function(){
        after_disabled_graph($(this));
    });
}

function init_web_filter_selector(selector, ext_filter, callback){
    if (selector.hasClass("inited")){return}
    var monitor_id = selector.closest(".chart").attr("data-monitor_id");
    var field = selector.find("input").last().attr("name");
    $.post(site_url+cc_biz_id+'/'+"operation/monitor/field/values/",
        {field:field, monitor_id:monitor_id, ext_filter:JSON.stringify(ext_filter), time_range:make_time_range()},
        function(res){
            if (res.result){
                selector.find("input").last().attr("placeholder", "请选择...").select2({
                    data: res.data
                });
                selector.addClass("inited")
            }else{
                selector.find("input").last().attr("placeholder", "请填写...")
            }
            if (callback){
                callback();
            }
        }, 'json');
}


function get_alerts_info(contain){
    var params = contain.find("div.chart-filter>form").serializeObject();
    params["time_range"] = make_time_range();
    var monitor_id = contain.attr("data-monitor_id");
    var monitor_backend_id = contain.attr("data-monitor_backend_id");
    params["monitor_id"] = monitor_id;
    var chart_obj = contain.find(".king-block-content-chart").highcharts();
    $.get(site_url+cc_biz_id+'/'+"operation/monitor/alert/list/", params, function(res){
        if (res.result){
            var alert_data = res.data;
            alert_list = [];
            // 一般
            var info_alerts = alert_data["3"];
            Array.prototype.push.apply(alert_list, info_alerts);
            // 预警
            var warning_alerts = alert_data["2"];
            Array.prototype.push.apply(alert_list, warning_alerts);
            // 严重
            var critical_alerts = alert_data["1"];
            Array.prototype.push.apply(alert_list, critical_alerts);
            // new 将一般，预警，严重的时间分成3条series加入到图表，fix 游览器卡死的问题
            var graph_point_info = {};
            // 将异常事件点对应的正常点找到
            for (var i=0; i<alert_list.length; i++){
                var alert = alert_list[i];
                if (!graph_point_info.hasOwnProperty(alert.source_timestamp)){
                    var series_index = 0;
                    var event_points = [];
                    for (var j=0; j<chart_obj.series.length; j++){
                        // 今日，同比，环比 3个点都拿到
                        var event_point = get_graph_nearest_timepoint(contain, j, alert.source_timestamp);
                        event_points.push(event_point);
                    }
                }
                graph_point_info[alert.source_timestamp] = event_points;
            }
            // 一般异常序列
            series_info = {
                1:{
                    event_dict: {},
                    timestamp_list: [],
                    data: []
                },
                2:{
                    event_dict: {},
                    timestamp_list: [],
                    data: []
                },
                3:{
                    event_dict: {},
                    timestamp_list: [],
                    data: []
                }
            };
            var interval = alert_data["interval"];
            // info
            for (i=0;i<info_alerts.length;i++){
                alert = info_alerts[i];
                var event_dict = series_info[alert.level].event_dict;
                var timestamp_list = series_info[alert.level].timestamp_list;
                var data = series_info[alert.level].data;
                event_dict[alert.source_timestamp] = alert;
                var alert_y = graph_point_info[alert.source_timestamp][0].y;
                if (alert_y==null){
                    alert_y = get_laster_point_y(contain);
                }
                if (timestamp_list.indexOf(alert.source_timestamp) >= 0){
                    // 判断是否是连续的点
                    // 是连续的点， 将data值的null改成正常点的值，同时新增下一个周期值为null的点。
                    data[data.length-1][1] = alert_y;

                    data.push([alert.source_timestamp + interval, null])

                }else{
                    // 不是连续的点,加入该点，同时新增下一周期值为null的点
                    timestamp_list.push(alert.source_timestamp);
                    data.push([alert.source_timestamp, alert_y]);

                    data.push([alert.source_timestamp + interval, null])
                }
                //给下个周期的点加上null的点
                timestamp_list.push(alert.source_timestamp+interval);
            }
            // critical
            for (i=0;i<critical_alerts.length;i++){
                alert = critical_alerts[i];
                event_dict = series_info[alert.level].event_dict;
                timestamp_list = series_info[alert.level].timestamp_list;
                data = series_info[alert.level].data;
                event_dict[alert.source_timestamp] = alert;
                alert_y = graph_point_info[alert.source_timestamp][0].y;
                if (alert_y==null){
                    alert_y = get_laster_point_y(contain);
                }
                if (timestamp_list.indexOf(alert.source_timestamp) >= 0){
                    // 判断是否是连续的点
                    // 是连续的点， 将data值的null改成正常点的值，同时新增下一个周期值为null的点。
                    data[data.length-1][1] = alert_y;

                    data.push([alert.source_timestamp + interval, null])

                }else{
                    // 不是连续的点,加入该点，同时新增下一周期值为null的点
                    timestamp_list.push(alert.source_timestamp);
                    data.push([alert.source_timestamp, alert_y]);

                    data.push([alert.source_timestamp + interval, null])
                }
                //给下个周期的点加上null的点
                timestamp_list.push(alert.source_timestamp+interval);
            }
            // warning
            for (i=0;i<warning_alerts.length;i++){
                alert = warning_alerts[i];
                event_dict = series_info[alert.level].event_dict;
                timestamp_list = series_info[alert.level].timestamp_list;
                data = series_info[alert.level].data;
                event_dict[alert.source_timestamp] = alert;
                alert_y = graph_point_info[alert.source_timestamp][0].y;
                if (alert_y==null){
                    alert_y = get_laster_point_y(contain);
                }
                if (timestamp_list.indexOf(alert.source_timestamp) >= 0){
                    // 判断是否是连续的点
                    // 是连续的点， 将data值的null改成正常点的值，同时新增下一个周期值为null的点。
                    data[data.length-1][1] = alert_y;

                    data.push([alert.source_timestamp + interval, null])

                }else{
                    // 不是连续的点,加入该点，同时新增下一周期值为null的点
                    timestamp_list.push(alert.source_timestamp);
                    data.push([alert.source_timestamp, alert_y]);

                    data.push([alert.source_timestamp + interval, null])
                }
                //给下个周期的点加上null的点
                timestamp_list.push(alert.source_timestamp+interval);
            }
            var chart_option = chart_obj.options;
            var refresh = false;
            for (level in series_info){
                if (series_info.hasOwnProperty(level) && series_info[level].data.length>0){
                    //add_alert_series(contain, series_info[level])
                    chart_option = make_alert_series_option(series_info[level], chart_option, monitor_backend_id);
                    refresh = true;
                }
            }
            var start_time = Date.now();
            if (refresh){
                // 等图标渲染完成，超时3秒
                var query_id = setInterval(function(){
                    if (!all(Object.keys(ready_info).map(function(key){return ready_info[key]})) && Date.now()-start_time < 3000){
                    }else{
                        chart_option.plotOptions.spline.animation = false;
                        contain.find(".king-block-content-chart").highcharts(chart_option);
                        clearInterval(query_id);
                    }
                }, 100);
            }
        }else{
            console.log("获取告警事件失败.");
        }
    }, 'json');
}
//function add_alert_series(contain, series_info){
//    // 添加告警点连成的线
//    var event_list = Object.keys(series_info.event_dict).map(function(key){return series_info.event_dict[key]});
//    if (event_list.length==0){return}
//    var event_demo = event_list[0];
//    // 根据series条数判断是否是过滤查询，过滤查询显示过滤过的时间，非过滤查询显示全部事件
//    var chart_obj = contain.find("div.king-block-content-chart").highcharts();
//    // add new series
//    var alert_series = chart_obj.addSeries({
//        zIndex: 10,
//        point: {
//            events: {
//                click: function(){
//                    var event = series_info.event_dict[this.x];
//                    var alarm_time = $("#daterangepicker").val();
//                    var alarm_id = event.alert_ids.join(",");
//                    var params = {
//                        alarm_time: alarm_time,
//                        alarm_id: alarm_id
//                    };
//                    //openDetailIframe("alarm/" + obj_to_query_string(params))
//                    window.location.href = site_url+cc_biz_id+'/alarm/'+ obj_to_query_string(params);
//                }
//            }
//        },
//        cursor: 'pointer',
//        marker: {
//            symbol: 'circle',
//            radius: 2
//        },
//        color: event_color(event_demo.level.toString()),
//        name: event_demo.id,
//        data: series_info.data,
//        showInLegend: false,
//        tooltip: {
//            followPointer: false,
//            followTouchMove: false,
//            pointFormatter: function(){
//                var event = series_info.event_dict[this.x];
//                if (!event){return ""}
//                return '<tr><td>'+make_alert_count_display(event)+' </td></tr><br>'+
//                    '<tr><td>影响范围：'+event.dimensions_display+'</td></tr>' +
//                    '<tr><td>告警描述：'+event.raw+'</td></tr>'+
//                    '<tr><td><br> </td></tr>'+
//                    '<tr><td><b>点击图表中的异常点，查看详细告警内容。</b></td></tr>';
//            }
//        }
//    }, true);
//}

function make_alert_series_option(series_info, option, monitor_id){
    // 生成告警序列的series配置
    var event_list = Object.keys(series_info.event_dict).map(function(key){return series_info.event_dict[key]});
    if (event_list.length==0){return option}
    var event_demo = event_list[0];
    var series_opt = {
        zIndex: 10,
        point: {
            events: {
                click: function(){
                    var event = series_info.event_dict[this.x];
                    var params = {
                        start_time: event.source_time,
                        end_time: event.source_time,
                        monitor_id: monitor_id
                    };
                    //openDetailIframe("alarm/" + obj_to_query_string(params))
                    //window.location.href = site_url+cc_biz_id+'/alarm/'+ obj_to_query_string(params);
                    window.location.href = site_url+cc_biz_id+'/event_center/'+ obj_to_query_string(params);
                }
            }
        },
        cursor: 'pointer',
        marker: {
            symbol: 'circle',
            radius: 3
        },
        color: event_color(event_demo.level.toString()),
        name: event_demo.id,
        data: series_info.data,
        showInLegend: false,
        tooltip: {
            followPointer: false,
            followTouchMove: false,
            pointFormatter: function(){
                var event = series_info.event_dict[this.x];
                if (!event){return ""}
                return '<tr><td>'+make_alert_count_display(event)+' </td></tr><br>'+
                    '<tr><td>影响范围：'+event.dimensions_display+'</td></tr>' +
                    '<tr><td>告警描述：'+event.raw+'</td></tr>'+
                    (event.extend_message?'<tr><td>辅助参考：'+event.extend_message+'</td></tr>':"")+
                    '<tr><td><br> </td></tr>'+
                    '<tr><td><b>点击图表中的异常点，查看详细告警内容。</b></td></tr>';
            }
        }
    };
    var alert_timestamp_list = [];
    for (var i=0;i<series_info.data.length;i++){
        if (series_info.data[i][1] != null){
            alert_timestamp_list.push(series_info.data[i][0])
        }
    }
    // 移除异常点时间对应的正常点
    for (i=0;i<3;i++){
        var new_series = [];
        for (var j=0; j<option.series[i].data.length;j++){
            var point_data = option.series[i].data[j];
            if (alert_timestamp_list.indexOf(point_data[0]) < 0){
                new_series.push(point_data);
            }else{
                if (i==0){
                    // 本周期的点设置为nul, 其他周期的点直接移除
                    new_series.push([point_data[0], null]);
                }
            }
        }
        option.series[i].data = new_series
    }
    option.series.push(series_opt);
    return option
}

function level_html_display(event){
    return make_color_text(event_color(event.level), event.level_display);
}
function make_color_text(color, text){
    return '<span style="color:'+color+';">'+text+'</span>';
}
function make_alert_count_display(event){
    // 生成告警事件条数说明
    var level_display = {
        1: make_color_text(event_color(1), '【严重】'),
        2: make_color_text(event_color(2), '【普通】'),
        3: make_color_text(event_color(3), '【轻微】')
    };
    if (event.alert_count == 1){
        return "发生一条"+ level_display[event.level] + "告警";
    }
    var alert_count_info = event.alert_count_info;
        var msg = "同时发生多条告警<br>共计：";
        var sep_count = 0;
        for (var i=1; i<=3; i++){
            if (alert_count_info[i] > 0){
                msg = msg + (sep_count==0?" ":" / ") + alert_count_info[i] + "条" + level_display[i];
                sep_count = 1;
            }
        }
    return msg
}
// 添加事件图标  update by willgchen 5-21 由前端聚合改成后台聚合。 update 5-24 此方法在点多的时候会使浏览器崩溃.
//function add_alert_point(contain, event_info){
//    var event = event_info.alert;
//    var count = event.alert_count;
//    var alert_point = event_info.event_points[0];
//    var panel = contain.find("div.king-block-content-chart");
//    // 根据series条数判断是否是过滤查询，过滤查询显示过滤过的时间，非过滤查询显示全部事件
//    var chart_obj = $(panel).highcharts();
//    // add new series
//    var alert_series = chart_obj.addSeries({
//        zIndex: 10,
//        point: {
//            events: {
//                click: function(){
//                    var alarm_time = $("#daterangepicker").val();
//                    var alarm_id = event.alert_ids.join(",");
//                    var params = {
//                        alarm_time: alarm_time,
//                        alarm_id: alarm_id
//                    };
//                    window.location.hash = '#alarm/';
//                    //openDetailIframe("alarm/" + obj_to_query_string(params))
//                    window.location.href = site_url+cc_biz_id+'/alarm/'+ obj_to_query_string(params);
//                }
//            }
//        },
//        cursor: 'pointer',
//        marker: {
//            symbol: 'circle',
//            radius: 3
//        },
//        color: event_color(event.level.toString()),
//        name: event.id,
//        data: [[alert_point.x, alert_point.y]],
//        showInLegend: false,
//        tooltip: {
//            followPointer: false,
//            followTouchMove: false,
//            pointFormatter: function(){
//                return '<tr><td>'+make_alert_count_display(event)+' </td></tr><br>'+
//                    '<tr><td>影响范围：'+event.dimensions_display+'</td></tr>' +
//                    '<tr><td>告警描述：'+event.raw+'</td></tr>'+
//                    '<tr><td><br> </td></tr>'+
//                    '<tr><td><b>点击图表中的异常点，查看详细告警内容。</b></td></tr>';
//            }
//        }
//    }, false);
//    for (var i=0; i < event_info.event_points.length; i++){
//        event_info.event_points[i].remove();
//    }
//
//
//}
function get_laster_point_y(contain){
    //获取图表中，最新的值。
    var chart_obj = contain.find(".king-block-content-chart").highcharts();
    var y_list = chart_obj.series[0].yData.slice();
    y_list.reverse();
    for (var i=0;i<y_list.length;i++){
        if (y_list[i]!=null){
            return y_list[i]
        }
    }
    return null
}
function get_graph_nearest_timepoint(contain, series_index, timepoint){
    var chart_obj = contain.find(".king-block-content-chart").highcharts();
    // 获取图表上，时间点最接近的时间点
    var _sort_array = [];
    $.extend(_sort_array, chart_obj.series[series_index].xData);
    _sort_array.push(timepoint);
    _sort_array.sort(function(a, b){return a-b});
    var xaxis_index = _sort_array.indexOf(timepoint);
    return chart_obj.series[series_index].points[xaxis_index];
}

function add_graph_to_panel(html){
    var dom = $(html);
    var last_chart = $($(".chart-contain").slice(-1));
    if (last_chart.length>0){
        last_chart.after(dom);
    }else{
        $(".chart").first().before(dom);
    }
    alert_topbar("接入成功", "ok");
    bind_panel_event();
    make_contain_graph(dom);
}

function iframeCallBack(monitor_id){
    // iframe 回调
    if (monitor_id){
        if (callback_code == 2){
            $.post(site_url+cc_biz_id+'/'+"operation/monitor/location/add/", {monitor_id: monitor_id, menu_id:menu_id}, function(res){
                if (res.result){
                    add_graph_to_panel(res.data.html)
                }else{
                    app_alert(res.message, "fail");
                    // 提示监控对应的图表
                    var contain = $(".chart-contain[data-monitor_id="+monitor_id+"]")[0];
                    make_contain_graph($(contain));
                }
            }, 'json');
        }
        if (callback_code == 1){
            //$(".charts-container").find(".chart-contain[data-monitor_id=100]");
            var contains = $(".charts-container").find(".chart-contain[data-monitor_id="+monitor_id+"]");
            for (var i=0;i<contains.length;i++){
                update_graph_title($(contains[i]))
            }
        }
    }
}

function update_graph_title(contain){
    var monitor_id = contain.attr("data-monitor_id");
    $.get(site_url+cc_biz_id+"/operation/monitor/info/",{monitor_id: monitor_id}, function(res){
        if (res.result){
            var monitor = res.data;
            contain.find(".monitor-title").text(monitor.monitor_name)
        }
    }, "json");

}

function show_loading(contain){
    contain.find(".king-block-content-chart").html('<img alt="loadding" src="'+static_url+'img/hourglass_36.gif" style="margin-top: 100px;margin-left:45%;">');
}

function hide_loading(contain){
    contain.find(".king-block-content-chart").html("");
}
function add_shadow(contain){
    if (contain.find(".king-block-header").find("div").length >0){
        return
    }
    var shadow_div = $($shadow);
    shadow_div.prependTo(contain.find(".king-block-header")).find("a").on("click", function(e){
        app_confirm("是否确认启用", function(){
            active_monitor(contain, shadow_div);
        });

    });
}
function active_monitor(contain, shadow_div){
    var monitor_id = contain.attr("data-monitor_id");
    $.post(site_url+cc_biz_id+"/config/operate_monitor/"+monitor_id+ '/', {is_enabled:1}, function(res){
        if (res.result){
            shadow_div.remove();
            after_active_graph(contain);
        }else{
            app_alert(res.message, "fail");
        }
    }, 'json');
    return false;
}

function after_active_graph(contain){
    contain.attr("data-enabled", "1");
    contain.find(".m_disabled").closest("li").show();
    contain.find(".refresh").unbind("click").css("cursor", "pointer").on('click', function(e){
        make_contain_graph(contain);
    }).attr("title", "刷新");
    contain.find(".chart-filter-btn").unbind("click").css("cursor", "pointer").on("click", function(e){
        $(e.target).closest("button").toggleClass("expand");
        $(e.target).closest(".king-block-header").next().slideToggle("fast");
    }).attr("title", "条件过滤");
    alert_topbar("监控启用成功", "ok");
}
