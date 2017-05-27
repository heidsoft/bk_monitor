/**
 * Created by willgchen on 2016/5/22.
 */

$err_div = '<div class="p20 pt20" style="height:100%;">'+
    '<div class="alert alert-warning" role="alert" style="height:100%;max-height: 280px;overflow:auto;">'+
      '<p id="error_title" class="mb10"><b>获取数据失败：</b></p>'+
      '<p id="error_msg">SQL查询失败：原因：结果表 112_ja_online 不存在</p>'+
      '<p>SQL:</p>'+
    '</div>'+
'</div>';
var page = 1;
var star_chart_panel = $('.star-chart-panel');
var total_star_graphs_pages = 1;
Highcharts.setOptions(Highcharts.theme_default);


$('.page-prev').click(function() {
    if ($(this).closest("a").hasClass("king-disabled")){
        return
    }
    render_star_contains(page-1);
});
$('.page-next').click(function() {
    if ($(this).closest("a").hasClass("king-disabled")){
        return
    }
    render_star_contains(page+1);
});
$('.page-refresh').click(function(event) {
    make_graphs();
});


function bind_modal_event(){
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
    $("button.favorite").unbind("hover").hover(function(e){
        var a_dom = $(e.target).closest("button");
        if (!a_dom.hasClass("active")){
            a_dom.addClass("hover");
        }
    }, function(e){
        var a_dom = $(e.target).closest("button");
            a_dom.removeClass("hover");
    }).unbind("click").on("click", function(e){
        var monitor_id = $(e.target).closest(".chart-one").attr("data-monitor_id");
        app_confirm("是否确认取消关注？", function(){
            $.post(site_url+cc_biz_id+'/'+"operation/monitor/favorite/toggle/", {monitor_id:monitor_id}, function(res){
                if (res.result){
                    alert_topbar("取消关注成功", "ok");
                    render_star_contains(page);
                }else{
                    app_alert(res.message, "fail");
                }
            }, "json");
        });
    });
}

function show_star_loading(){
    star_chart_panel.html('<img alt="loadding" class="loading-img" src="http://o.qcloud.com/static_api/v3/components/loading1/images/loading_2_36x36.gif">');
}
function render_star_contains(page_num){
    // 分页渲染我的关注页
    if(!page_num){
        page_num = 1;
    }
    page = (page_num % total_star_graphs_pages)==0?total_star_graphs_pages:(page_num % total_star_graphs_pages);
    show_star_loading();
    $.get(site_url+cc_biz_id+"/overview/star/panel/", {page:page}, function(res){
        star_chart_panel.html(res);
        bind_modal_event();
        make_graphs();
        update_paging_button();
    });
}
function update_paging_button(){

    var prev_button = $(".page-btn-group").find(".page-prev");
    var next_button = prev_button.next();
    if (page==1){
        prev_button.addClass("king-disabled");
    }else{
        prev_button.removeClass("king-disabled");
    }
    if (page==total_star_graphs_pages){
        next_button.addClass("king-disabled");
    }else{
        next_button.removeClass("king-disabled");
    }
}

function make_graphs(){
    var contains = star_chart_panel.find(".chart-one");
    for (var i=0; i<contains.length; i++){
        var contain = contains[i];
        make_contain_graph($(contain))
    }
}
function show_graph_loading(contain){
    contain.find("div.charts-line-panel").html('<img alt="loadding" src="'+static_url+'img/hourglass_36.gif" style="margin-top: 100px;margin-left:45%;">');
}
function hide_graph_loading(contain){
    contain.find("div.charts-line-panel").html("");
}
function make_contain_graph(contain){
    var graph_panel = contain.find("div.charts-line-panel");
    var monitor_id = contain.attr("data-monitor_id");
    if (!monitor_id){
        return
    }
    // 事件统计label初始化
    contain.find("label").html('<i class="fa fa-spinner fa-pulse mr5"></i>').css("cursor", "default").unbind("click");
    var params = {monitor_id: monitor_id, time_range: make_time_range()};
    //contain.find(".loading").show();
    show_graph_loading(contain);
    $.get(site_url+cc_biz_id+'/'+'operation/monitor/graph/point/', params, function(res){
        hide_graph_loading(contain);
        if(res.result){
            Hchart.make_graph(res.data.data, graph_panel[0], monitor_id);
            //加载完图表后再加载告警事件，显示在图表上。
            get_alerts_info(contain);
        }else{
            graph_panel.html("");
            var err_div = $($err_div).appendTo(graph_panel);
            err_div.find("#error_msg").text(res.message).next().text(res.data.echo_sql!==""?("SQL: " + res.data.echo_sql): "");
            if (res.data.error_class == "info"){
                err_div.find("#error_title").text("");
                err_div.find("#error_msg").css({"text-align": "center","margin-top": "50px"});
            }
        }
    }, 'json');
    if (contain.attr("data-enabled") == "0"){
        add_shadow(contain);
    }
}

function add_graph_to_panel(html){
    alert_topbar("添加关注成功", "ok");
    render_star_contains(page);
}
function get_laster_point_y(contain){
    //获取图表中，最新的值。
    var chart_obj = contain.find(".charts-line-panel").highcharts();
    var y_list = chart_obj.series[0].yData.slice();
    y_list.reverse();
    for (var i=0;i<y_list.length;i++){
        if (y_list[i]!=null){
            return y_list[i]
        }
    }
    return null
}
function get_alerts_info(contain){
    var params = {};
    params["time_range"] = make_time_range();
    var monitor_id = contain.attr("data-monitor_id");
    var monitor_backend_id = contain.attr("data-monitor_backend_id");
    params["monitor_id"] = monitor_id;
    var chart_obj = contain.find(".charts-line-panel").highcharts();
    $.get(site_url+cc_biz_id+'/'+"operation/monitor/alert/list/", params, function(res){
        if (res.result){
            var alert_data = res.data;
            alert_list = [];
            // 一般
            var info_alerts = alert_data["3"];
            Array.prototype.push.apply(alert_list, info_alerts);
            var info_alert_count = 0;
            var info_alert_ids = [];
            for (i=0;i<info_alerts.length;i++){
                info_alert_count = info_alert_count + info_alerts[i].alert_count;
                Array.prototype.push.apply(info_alert_ids, info_alerts[i].alert_ids);
            }
            contain.find("label.event-info").text(info_alert_count).css("cursor", "pointer").unbind("click").on("click", function(){
                var params = {
                    start_time: make_time_range().split(" -- ")[0]+":00",
                    end_time: make_time_range().split(" -- ")[1]+":00",
                    alarm_level: 3,
                    monitor_id: monitor_backend_id
                };
                //openDetailIframe("alarm/" + obj_to_query_string(params))
                window.location.href = site_url+cc_biz_id+'/event_center/'+ obj_to_query_string(params);
            });
            // 预警
            var warning_alerts = alert_data["2"];
            Array.prototype.push.apply(alert_list, warning_alerts);
            var warning_alert_count = 0;
            var warning_alert_ids = [];
            for (i=0;i<warning_alerts.length;i++){
                warning_alert_count = warning_alert_count + warning_alerts[i].alert_count;
                Array.prototype.push.apply(warning_alert_ids, warning_alerts[i].alert_ids);
            }
            contain.find("label.event-warning").text(warning_alert_count).css("cursor", "pointer").unbind("click").on("click", function(){
                var params = {
                    start_time: make_time_range().split(" -- ")[0]+":00",
                    end_time: make_time_range().split(" -- ")[1]+":00",
                    alarm_level: 2,
                    monitor_id: monitor_backend_id
                };
                //openDetailIframe("alarm/" + obj_to_query_string(params))
                window.location.href = site_url+cc_biz_id+'/event_center/'+ obj_to_query_string(params);
            });
            // 严重
            var critical_alerts = alert_data["1"];
            Array.prototype.push.apply(alert_list, critical_alerts);
            var critical_alert_count = 0;
            var critical_alert_ids = [];
            for (i=0;i<critical_alerts.length;i++){
                critical_alert_count = critical_alert_count + critical_alerts[i].alert_count;
                Array.prototype.push.apply(critical_alert_ids, critical_alerts[i].alert_ids);
            }
            contain.find("label.event-danger").text(critical_alert_count).css("cursor", "pointer").unbind("click").on("click", function(){
                var params = {
                    start_time: make_time_range().split(" -- ")[0]+":00",
                    end_time: make_time_range().split(" -- ")[1]+":00",
                    alarm_level: 1,
                    monitor_id: monitor_backend_id
                };
                //openDetailIframe("alarm/" + obj_to_query_string(params))
                window.location.href = site_url+cc_biz_id+'/event_center/'+ obj_to_query_string(params);
            });
            // 已处理
            var handled_alerts = alert_data["handled"];
            // 未处理
            var unhandled_alerts = alert_data["unhandled"];
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
                        contain.find(".charts-line-panel").highcharts(chart_option);
                        clearInterval(query_id);
                    }
                }, 100);
            }
        }else{
            console.log("获取告警事件失败.");
        }
    }, 'json');
}


function get_graph_nearest_timepoint(contain, series_index, timepoint){
    var chart_obj = contain.find(".charts-line-panel").highcharts();
    // 获取图表上，时间点最接近的时间点
    var _sort_array = [];
    $.extend(_sort_array, chart_obj.series[series_index].xData);
    _sort_array.push(timepoint);
    _sort_array.sort(function(a, b){return a-b});
    var xaxis_index = _sort_array.indexOf(timepoint);
    return chart_obj.series[series_index].points[xaxis_index];
}

function make_today_time_range(){
    var today = new Date();
    var thisMonth = today.getMonth() + 1;
    if(thisMonth<10) thisMonth = "0" + thisMonth;
    var yyyymmdd = today.getFullYear() + "-" + thisMonth  + "-" + today.getDate();
    return yyyymmdd + " 00:00 -- " + yyyymmdd + " 23:59"
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


$shadow = '<div class="shadow" style="position: absolute;text-align: center;padding-top: 110px;z-index: 2;margin: -15px;margin-top: 11px;width: 100%;height: 250px;background-color: rgba(38,50,56,0.5);font-size: 20px;color: #020202;font-weight: 800;"><a href="###" style="color: #f5f5f5;">监控被禁用，点击启用</a></div>';

function add_shadow(contain){
    if (contain.find(".panel-default").find("div.shadow").length >0){
        return
    }
    var shadow_div = $($shadow);
    contain.find(".portlet-header").find("span").after(shadow_div);
    shadow_div.find("a").on("click", function(e){
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
            contain.attr("data-enabled", "1")
        }else{
            app_alert(res.message, "fail");
        }
    }, 'json');
    return false;
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
                    window.location.href = site_url+cc_biz_id+'/event_center/'+ obj_to_query_string(params);
                }
            }
        },
        cursor: 'pointer',
        marker: {
            symbol: 'circle',
            radius: 2
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
                    '<tr><td>辅助参考：'+event.extend_message+'</td></tr>'+
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