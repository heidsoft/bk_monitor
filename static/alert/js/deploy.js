var wait_data = [{"id":"", "text": "数据待加载"}];

// 确认弹框
function app_confirm(msg, callback) {
    dialog({
        width: 260,
        title: '确认',
        content: msg,
        okValue: '确定',
        ok: function() {callback()},
        cancelValue: '取消',
        cancel: function() {}
    }).show();
}

// 提示弹框
function app_alert(msg, type) {
    dialog({
        width: 260,
        title: '提示',
        cancel: function (){},
        ok: function() {},
        okValue: '确定',
        cancel: false,
        content: '<div class="king-notice-box king-notice-'+type+'"><p class="king-notice-text">'+msg+'</p></div>'
    }).show();
}

// 所有维度字段
var dimension_data = wait_data;

// 初始化 select2
$("select.select2").select2({dropdownAutoWidth:"true"});
$("input.select2").select2({data:wait_data, dropdownAutoWidth:"true"});


// 收缩
$(".toggle-panel").on("click", function(){
    $(this).children(".fa").toggle();
    $("#panel-"+$(this).attr("data")).toggle();
})


// 转化统计配置方式
$(".toggle_group_type").on("click", function(){
    $(".toggle_group_type").toggle();
    $(".form-group-toggle").toggle();
})


// 更新 bksql 的可用字段
function set_bksql_dimension(){
    var html = "";
    for (var i = 1; i < dimension_data.length; i ++){
        html += dimension_data[i].text + ", ";
    }
    $("#sql_dimension_field").html(html.slice(0, -2));
}


// 表单提交参数封装
function get_submit_param(){
    var param = {};
    var tr_a = [];
    var tr_b = [];
    param.src_type=src_type;
    param.sensitive="1";
    param.biz_id=cc_biz_id;
    param.monitor_conditions = [];
    param.monitor_id = monitor_id;

    // 监控名称
    param.monitor_name = $("#monitor_name").val();
    if (!param.monitor_name){app_alert("必填参数未填：监控名称");return}
    if (param.monitor_name.length > 30){app_alert("监控名称不能超过30个字符");return}

    // 标签
    param.tags = $("#tags").val();
    if (!param.tags){app_alert("必填参数未填：监控标签");return}

    // DB 数据接入
    if ($("#data_src").val() == "db"){
        param.db_host = $("#db_host").val();
        if (!param.db_host){app_alert("必填参数未填：数据库HOST/域名");return}
        param.db_port = $("#db_port").val();
        if (!param.db_port){app_alert("必填参数未填：数据库端口");return}
        param.db_name = $("#db_database").val();
        if (!param.db_name){app_alert("必填参数未填：数据库库名");return}
        param.table_name = $("#db_table").val();
        if (!param.table_name){app_alert("必填参数未填：数据库表名");return}
        param.character_set = $("#encoding").val();
        if (!param.character_set){app_alert("必填参数未填：数据库编码");return}
        param.before_time = 300;
        param.interval = 20;
        param.time_field = $("#time_field").val();
        if (!param.time_field){app_alert("必填参数未填：时间字段");return}
        param.time_format = $("#time_field_format").val();
        if (!param.time_format){app_alert("必填参数未填：时间字段格式");return}
        param.access_type = "db";
    } else if ($("#data_src").val() == "trt"){
        if (!$("#data_table").val()){app_alert("必填参数未填：数据");return}
        if ($("#data_table").select2("data").type == "trt"){
            param.result_table_id = $("#data_table").val()
            param.access_type = "trt"
        } else {
            param.dataid = $("#data_table").val()
            param.dataset = $("#data_table").select2("data").dataset
            param.data_format_id = $("#data_table").select2("data").data_format
            param.access_type = "dataset"
            param.time_field = $("#time_field").val();
            if (!param.time_field){app_alert("必填参数未填：时间字段");return}
            param.time_format = $("#time_field_format").val();
            if (!param.time_format){app_alert("必填参数未填：时间字段格式");return}
        }
    }
    // 获取统计方式配置
    param = get_group_config(param);
    if (!param){return}

    $("#config_tbody tr").each(function(){
        var monitor_config = {}
        var trid = $(this).attr("id")
        //区分该行属于策略信息或通知配置 tr-a: 策略信息; tr-b: 通知配置
        if($(this).attr("class") == "tr-a"){
            monitor_config.config_id = parseInt($("#" + trid).attr("config_id"))
            monitor_config.condition_id = parseInt($("#" + trid).attr("condition_id"))
            monitor_config.alarm_def_id = parseInt($("#" + trid).attr("alarm_def_id"))
            monitor_config.strategy_id = $("#" + trid + " #config_type").val()
            monitor_config.strategy_option = get_strategy_option(trid, monitor_config.strategy_id)
            if (!monitor_config.strategy_option){app_alert("必填参数未填：策略参数");return}
            monitor_config.condition = get_monitor_condition(trid)
            monitor_config.monitor_level = $("#" + trid + " #monitor_level").val()
            if (!monitor_config.monitor_level){app_alert("必填参数未填：告警级别");return}
            tr_a.push(monitor_config)
        }
        else if($(this).attr("class") == "tr-b"){
            if($("#" + trid + " #use_full_config").is(":checked")){
                monitor_config = get_alarm_def_config("full_config", true)
            }
            else{
                monitor_config = get_alarm_def_config(trid, false)
            }
            tr_b.push(monitor_config)
        }
    })

    $.each(tr_a, function(index, value){
        param.monitor_conditions.push($.extend({}, tr_a[index], tr_b[index]))
    })
    if (param.monitor_conditions.length==0){app_alert("必填参数未填：至少要有一个监控配置");return}
    console.debug(param.monitor_conditions)

    return param
}


function get_group_config(param){
    // 配置模块
    if($("#bksql-form").css("display") == "none"){
        param.group_type = 'form';
        param.bksql = "";
        if (!$("#monitor_field").val()){app_alert("必填参数未填：监控字段");return}
        param.count_field = {"name": $("#monitor_field").val(), "type": $("#monitor_field").select2("data").type, "desc": $("#monitor_field").select2("data").desc}
        if ($("#data_table").select2("data") && $("#data_table").select2("data").type != "trt"){
            param.count_method = $("#count_method").val();
            if (!param.count_method){app_alert("必填参数未填：统计方式");return}
        }
        param.dimension_fields = $("#dimension_field").select2("data");
        param.count_freq = $("#count_freq_group").val();
    // BKSQL 模块
    } else {
        param.group_type = 'bksql';
        param.bksql = $("#bksql").val();
        param.count_method = "count"
        param.dimension_fields = []
        param.count_field = {}
        if (!param.bksql){app_alert("必填参数未填：BKSQL");return}
        param.count_freq = $("#count_freq_sql").val();
    }
    if (!param.count_freq){app_alert("必填参数未填：监控周期");return}
    return param;
}


function get_alarm_def_config(trid, is_global){
    var alarm_def_config = {}
    alarm_def_config.is_global = is_global
    alarm_def_config.notify = {"role_list": []}
    $("#" + trid + " input[name='notify']:checked").each(function () {
        if(this.value == "phone_failure"){
            alarm_def_config.notify["failure_notify_phone"] = true
        }
        else{
            alarm_def_config.notify["begin_notify_" + this.value] = true
            alarm_def_config.notify["success_notify_" + this.value] = true
            alarm_def_config.notify["failure_notify_" + this.value] = true
        }
    })
    $("#" + trid + " input[name='role']:checked").each(function () {
        alarm_def_config.notify["role_list"].push(this.value)
        if(this.value == "PmpDBAMajor"){
            alarm_def_config.notify["role_list"].push("PmpDBABackup")
        }
    })
    if($("#" + trid + " #extra").is(":checked")){
        if(trid == 'full_config'){
            alarm_def_config.responsible = $("#" + trid + " #full_config_member").val()
        }
        else{
            alarm_def_config.responsible = $("#" + trid + " #" + trid + "member").val()
        }
    }
    else{
        alarm_def_config.responsible = ""
    }
    alarm_def_config.solution_id = $("#" + trid + " #solution_id").val()
    return alarm_def_config
}


//获取策略具体参数 trid: 所属策略tr行id; config_type: 策略类型
function get_strategy_option(trid, config_type){
    var strategy_option = {}
    console.debug(trid)
    if(config_type == "2"){
        strategy_option.continuous = $("#" + trid + " #config_" + config_type + " #continuous").val()
        strategy_option.trend = $("#" + trid + " #config_" + config_type + " #trend").val()
        strategy_option.threshold = $("#" + trid + " #config_" + config_type + " #threshold").val()
    }
    else if(config_type == "10"){
        strategy_option.continuous = $("#" + trid + " #config_" + config_type + " #continuous").val()
        strategy_option.ratio = $("#" + trid + " #config_" + config_type + " #ratio").val()
        strategy_option.shock = $("#" + trid + " #config_" + config_type + " #shock").val()
        strategy_option.baseline = $("#" + trid + " #config_" + config_type + " #baseline").val()
    }
    else if(config_type == "11"){
        strategy_option.trend = $("#" + trid + " #config_" + config_type + " #trend").val()
        strategy_option.times = $("#" + trid + " #config_" + config_type + " #times").val()
        strategy_option.back_days = $("#" + trid + " #config_" + config_type + " #back_days").val()
        strategy_option.baseline = $("#" + trid + " #config_" + config_type + " #baseline").val()
    }
    else if(config_type == "12"){
        strategy_option.trend = $("#" + trid + " #config_" + config_type + " #trend").val()
        strategy_option.ratio = $("#" + trid + " #config_" + config_type + " #ratio").val()
        strategy_option.back_days = $("#" + trid + " #config_" + config_type + " #back_days").val()
        strategy_option.baseline = $("#" + trid + " #config_" + config_type + " #baseline").val()
    }
    return strategy_option
}


//获取过滤条件 trid: 所属策略tr行id
function get_monitor_condition(trid){
    var condition_list = []
    $("#" + trid + " .condition-div").each(function(){
        var condition_id = $(this).attr("id")
        var condition_item = {}
        condition_item.field = $("#" + condition_id + " #condition_field").val()
        condition_item.method = $("#" + condition_id + " #condition_expr").val()
        condition_item.value = $("#" + condition_id + " #condition_value").val()
        condition_list.push(condition_item)
    })
    return condition_list
}


// 获取所有MYSQL DATABASE
function get_mysql_database(){
    if (!$("#db_host").val() || !$("#db_host").val()){return}
    $("#db_data_loadding").toggle();
    $.ajax({
        url: site_url+"api/trt/show_databases/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            host: $("#db_host").val(),
            port: $("#db_port").val(),
        },
        success: function(result){
            if (result.result){
                var data = [];
                $.each(result.data, function (index, value) {
                    data.push({"id": value, "text":value});
                })
            } else {
                var data = [{"id": "", "text": "获取数据源失败:"+result.message}];
            }
            $("#db_database").select2({data:data, dropdownAutoWidth:"true"});
            $("#db_data_loadding").toggle();
        }
    })
}


// 获取所有MYSQL TABLE
function get_mysql_table(){
    $("#db_data_loadding").toggle();
    $.ajax({
        url: site_url+"api/trt/show_tables/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            host: $("#db_host").val(),
            port: $("#db_port").val(),
            database: $("#db_database").val(),
        },
        success: function(result){
            if (result.result){
                var data = [];
                $.each(result.data, function (index, value) {
                    data.push({"id": value, "text":value});
                })
            } else {
                var data = [{"id": "", "text": "获取数据源失败:"+result.message}];
            }
            $("#db_table").select2({data:data, dropdownAutoWidth:"true"});
            $("#db_data_loadding").toggle();
        }
    })
}


// 获取所有MYSQL TABLE
function get_mysql_field(){
    $("#db_data_loadding").toggle();
    $.ajax({
        url: site_url+"api/trt/list_table_fields/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            host: $("#db_host").val(),
            port: $("#db_port").val(),
            database: $("#db_database").val(),
            table: $("#db_table").val(),
        },
        success: function(result){
            if (result.result){
                dimension_data = [];
                var monitor_data = [{"id": "*", "text": "COUNT(*)"}];
                $.each(result.data, function (index, value) {
                    if (!value["desc"]){
                        var text = value["field"] + "(" + value['desc'] + ")";
                    } else {
                        var text = value["field"]
                    }
                    // 监控字段
                    monitor_data.push({id: value["field"], type: value["type"], text: text})
                    // 维度字段
                    dimension_data.push({id: value["field"], text: text})
                })
            } else {
                dimension_data = [{"id": "", "text": "获取数据源失败:"+result.message}];
                var monitor_data = [{"id": "", "text": "获取数据源失败:"+result.message}];
            }
            $("#db_data_loadding").toggle();
            // 时间字段
            $("#time_field").select2({data:dimension_data, dropdownAutoWidth:"true"});
            $("#time_field").select2("val", null);
            // 维度字段
            $("#dimension_field").select2({data:dimension_data, multiple:true, dropdownAutoWidth:"true"});
            $("#dimension_field").select2("val", null);
            // 监控字段
            $("#monitor_field").select2({data:monitor_data, dropdownAutoWidth:"true"});
            $("#monitor_field").select2("val", null);
            // BKSQL 可用字段
            set_bksql_dimension();
        }
    })
}


// 获取所有数据平台结果表
var gem_data = [];
var group_data = [];
function get_result_table(){
    $.ajax({
        url: site_url+"api/trt/list_result_table_detail/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            result_table_list: result_table_list,
        },
        success: function(result){
            console.log(result);
            if (result.result){
                var data = [];
                $.each(result.data, function (index, value) {
                    console.log(value["description"]);
                    if (value["description"]){
                        var text = value["id"] + "(" + value["description"] + ")";
                    } else {
                        var text = value["id"]
                    }
                    $.each(JSON.parse(result_table_list), function(i, v){
                        var value_ = value["id"];
                        console.log(v);
                        console.log(value_);
                        if (v == value_){
                            gem_data.push({
                                "id": value["id"],
                                "type": "trt",
                                "detail": JSON.stringify(value),
                                "text": text
                            });
                        }
                    })
                    data.push({
                        "id": value["id"],
                        "type": "trt",
                        "detail": JSON.stringify(value),
                        "text": text
                    });
                })
            }
            else {
                var data = [{"id": "", "text": "获取结果表失败:"+result.message}];
            }
            if (!gem_data.length == 0){
                group_data.push({"text":"GEM 已统计结果表", "children":gem_data});
                group_data.push({"text":"已统计结果表", "children":data});
            }
            else {
                group_data.push({"text":"已统计结果表", "children":data});
            }
            console.log(group_data);
            if (group_data.length == 3){
                group_data = [group_data[1], group_data[2], group_data[0]];
            }
            if (group_data.length == 2){
                if (gem_data.length == 0){
                    group_data = [group_data[1], group_data[0]];
                }
            }
            $("#data_table").select2({data:group_data, dropdownAutoWidth:"true"});
            $("#data_table_loadding").hide();
        },
    })
    $.ajax({
        url: site_url+"api/trt/list_datasets/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            set_type: "biz",
        },
        success: function(result){
            console.log("datasets");
            console.log(result);
            if (result.result){
                var data = [];
                $.each(result.data, function (index, value) {
                    if (value["data_desc"]){
                        var text = "【" + value["data_id"] + "】" + value["data_set"] + "(" + value["data_desc"] + ")";
                    } else {
                        var text = "【" + value["data_id"] + "】" + value["data_set"]
                    }
                    data.push({
                        "id": value["data_id"],
                        "type": "dataset",
                        "text": text,
                        "dataset": value["data_set"],
                        "data_format": value["data_format_id"],
                    });
                })
            }
            else {
                var data = [{"id": "", "text": "获取数据源失败:"+result.message}]
            }
            group_data.push({"text":"数据源", "children":data});
            if (group_data.length > 1){
                console.log(group_data);
                $("#data_table").select2({data:group_data, dropdownAutoWidth:"true"});
                $("#data_table_loadding").hide();
            }
        },
    })
}

// 初始化数据平台数据结果表的监控配置
function show_field_by_result_table(){
    if ($("#data_table").val()== ''){ return }
    var data = JSON.parse($("#data_table").select2("data").detail);
    dimension_data = [];
    var dimension_data_value = [];
    var monitor_data = [];
    console.log("show_field_by_result_table");
    console.log(data);
    var count_method = "";
    $.each(data.fields, function (index, value) {
        // 监控字段
        if(!value["is_dimension"] && value["field"] != "timestamp" && value["field"] != "offset"){
            monitor_data.push({"id": value["field"], text: value["field"]});
            count_method = value["processor"];
        // 维度字段
        } else if (value["is_dimension"]){
            dimension_data.push({id: value["field"], text: value["field"]});
            dimension_data_value.push(value["field"]);
        }
    });
    // 维度字段
    $("#dimension_field").select2({data:dimension_data, multiple:true});
    $("#dimension_field").select2("val", dimension_data_value).trigger("change");
    $("#dimension_field").attr("readonly", "readonly")
    // 监控字段
    $("#monitor_field").select2({data:monitor_data, dropdownAutoWidth:"true"});
    $("#monitor_field").select2("val", null);
    // 统计方式
    $("#count_method").select2("val", count_method);
    $("#count_method").attr("disabled", "disabled");
    // 统计周期
    $("#count_freq_group").select2("val", data.count_freq);
    $("#count_freq_group").attr("disabled", "disabled");
    // 把监控字段添加到维度字段方便策略参数配置使用
    for (var i = 1; i < monitor_data.length; i ++){
        dimension_data.push(monitor_data[i]);
    }
    // BKSQL 可用字段
    set_bksql_dimension();
}


// 初始化数据平台数据数据源的监控配置
function show_field_by_dataset(){
    if ($("#data_table").val()== ''){ return }
    $(".group-dataset").show();
    $.ajax({
        url: site_url+"api/trt/list_dataset_fields/",
        dataType: "json",
        data: {
            data_id: $("#data_table").val(),
            biz_id: cc_biz_id,
        },
        success: function(result){
            console.log(result);
            if (result.result){
                var monitor_data = [{"id": "*", "text": "COUNT(*)", "type": "int", "desc": "COUNT(*)"}];
                dimension_data = [];
                $.each(result.data, function (index, value) {
                    if (value["description"]){
                        var text = value["name"] + "(" + value["description"] + ")";
                    } else {
                        var text = value["name"]
                    }
                    // 监控字段
                    monitor_data.push({id: value["name"], type: value["type"], text: text, desc: value["description"]})
                    // 维度字段
                    dimension_data.push({id: value["name"], text: text, desc: value["description"]})
                });
            } else {
                dimension_data = [{"id": "", "text": "获取数据失败:"+result.message}];
            }
            // 时间字段
            $("#time_field").select2({data:dimension_data, dropdownAutoWidth:"true"});
            $("#time_field").select2("val", null);
            // 维度字段
            $("#dimension_field").select2({data:dimension_data, multiple:true, dropdownAutoWidth:"true"});
            $("#dimension_field").select2("val", null);
            // 监控字段
            $("#monitor_field").select2({data:monitor_data, dropdownAutoWidth:"true"});
            $("#monitor_field").select2("val", null);
            // BKSQL 可用字段
            set_bksql_dimension();
        }
    })
}

function get_cc_role(trid){
    var role_list = ["Maintainers"]
    $(trid + " input[name='role']:checked").each(function () {
        if(this.value != "Maintainers"){
            role_list.push(this.value)
        }
        if(this.value == "PmpDBAMajor"){
            role_list.push("PmpDBABackup")
        }
    })
    $.ajax({
        url: site_url+"api/trt/get_cc_role/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            role_list: JSON.stringify(role_list),
        },
        success: function(result){
            if(result.result){
                var show_list = "<div style='word-break: break-all;'>"
                $.each(result.data, function(index, value){
                    if(value && value != ""){
                        show_list += value + ';'
                    }
                });
                show_list += "</div>"
            }
            else{
                var show_list = ""
            }
            $(trid + " #show_responsible").attr("data-content", show_list)
        }
    })
}


// 切换 BKSQL 的显示
function bksql_show_change(){
    if ($("#data_src").val() == "db" || 
            $("#data_table").select2("data").type == "dataset"){
        if ($("#bksql-form").css("display") == "none"){
            $("#group_2_sql").show();
        } else {
            $("#sql_2_group").show();
        }
    } else {
        if ($("#group-form").css("display") == "none"){
            $("#sql_2_group").click();
        }
        $("#sql_2_group").hide();
        // $("#group_2_sql").hide();
    }
}


// 数据来源的切换
function change_data_src(){
    $(".group-src").hide();
    $(".group-"+$("#data_src").val()).show();
    $("#dimension_field").removeAttr("readonly");
    $("#count_method").removeAttr("disabled");
    $("#count_freq_group").removeAttr("disabled");
    bksql_show_change();
    $("#graph").hide();
}

// 初始化数据平台数据的监控配置
function change_data_table(){
    $(".group-dataset").hide();
    $("#monitor_field").select2({data:[{"id": "", "text": "数据加载中"}], dropdownAutoWidth:"true"});
    $("#monitor_field").select2("val", null);
    $("#monitor_field").val("");
    $("#dimension_field").select2({data:[], multiple:true, dropdownAutoWidth:"true"})
    $("#dimension_field").select2("val", null);
    $("#dimension_field").removeAttr("readonly");
    $("#count_method").removeAttr("disabled");
    $("#count_freq_group").removeAttr("disabled");
    if ($("#data_table").select2("data").type == "trt"){
        show_field_by_result_table();
        show_graph();
    } else {
        $("#graph").hide();
        show_field_by_dataset();
    }
    bksql_show_change();
}

// 如果是结果表显示曲线
function show_graph(){
    if (!$("#data_table").select2("data").type == "trt"){$("#graph").hide(); return}
    var result_table_id = $("#data_table").select2("val");
    var field = $("#monitor_field").select2("val");
    if (! (result_table_id && field)){$("#graph").hide(); return;}
    $.getJSON(site_url+"result_table_chart_data/", {
        result_table_id: result_table_id,
        field: field,
    }, function(feedback){
        if (!feedback.result) {return;}
        Highcharts.setOptions({global: { useUTC: false } });
        $('#graph-context').highcharts({
            chart: {
                height: 250
            },
            tooltip: {
                useHTML: true,
                crosshairs: [{
                    width: 1,
                    color: "#EEE"
                }],
                shared: true,
                valueSuffix: "",
                xDateFormat: '%Y-%m-%d %H:%M:%S',
            },
            title: {
                text: "",
                align: "right"
            },
            xAxis: {
                type: 'datetime',
                maxZoom: 24 * 3600000, // fourteen days
                title: {
                    text: null
                }
            },
            subtitle: {
                text: null
            },
            credits: {
                enabled: false
            },
            series: [{"data": feedback.data, "name": result_table_id}]
        })
        $("#graph").show();
    })
}

// 绑定 MYSQL 域名/端口/库名/表名 的变动
$("#db_host").on("change", function(){get_mysql_database()})
$("#db_port").on("change", function(){get_mysql_database()})
$("#db_database").on("change", function(){get_mysql_table()})
$("#db_table").on("change", function(){get_mysql_field()})

// 绑定监控字段的变动
$("#monitor_field").on("change", function(){
    $("#count_method").select2("readonly", false);
    if ($(this).val() == "*"){
        var monitor_field_name = "*";
        $("#count_method").select2("val", "count").trigger("change");
        $("#count_method").select2("readonly", true);
    } else {
        var monitor_field_name = $("#monitor_field").select2("data").text;
    }
    $("#monitor_field_show").html(monitor_field_name);
    show_graph();
})

// 绑定统计周期的变动
$("#count_method").on("change", function(){
    $("#count_method_show").html($(this).select2("data").text);
})

// 绑定分组字段的变动
$("#dimension_field").on("change", function(){
    var text = "";
    var data = $(this).select2("data");
    if (data.length == undefined){
        data = [data];
    }
    for (var i = 0; i < data.length; i ++){
        text = text + data[i].text + ", "
    }
    $("#dimension_field_show").html(text.slice(0, -2));
})

// 初始化数据平台数据的监控配置
$("#data_table").on("change", function(){change_data_table();})

// 绑定数据来源变动
$("#data_src").on("change", function(){change_data_src();})

// 初始化全局配置
function init_full_config(){
    $("#full_config").prepend($("#tr-b-0").html());
    $("#full_config .full_config_alert").hide();
    $("#full_config #member").attr("id", "full_config_member");
    $("#full_config_member").memberInput();
}

// GEM 特殊逻辑
if (!mysql_host_list.length == 0){
    $("#db_host").select2({
        createSearchChoice:function(term) {
            return {id:term, text:term};
        },
        data: mysql_host_list,
        width: 165,
   });
}


// 更改通知人
$(document).on("change", ".member_check", function(){
    // 对于额外通知人
    if ($(this).attr("data") == "extra"){
        // 是否显示额外通知人
        if ($(this).is(":checked")){
            $(this).parent().parent().parent().parent().parent().next().show();
        } else {
            $(this).parent().parent().parent().parent().parent().next().hide();
            $(this).parent().parent().parent().parent().parent().children(".member").val("");
        }
    }
    // 更新通知人名单
})

// 添加一个范围条件
var condition_num = 0;
function add_condition(dom){
    condition_num += 1;
    var td = $(dom).parent().parent();
    var condition_id = "condition-config-"+condition_num;
    var html = "<div class='mb5 condition-div' id='"+condition_id+"'>"+
        td.children("#condition-config-0").html()+
        "</div>"
    td.prepend(html)
    $("#"+condition_id).show();
    // 初始化 select2
    $("#"+condition_id+" .condition_select2").select2();
    // 初始化维度
    var dimension_data = [];
    var monitor_field = $("#monitor_field").val();
    if (monitor_field){
        dimension_data.push({id: monitor_field, text: monitor_field});
    }
    var time_field = $("#time_field").val();
    if (time_field){
        dimension_data.push({id: time_field, text: time_field});
    }
    var dimension_fields = $("#dimension_field").val().split(",");
    for (var i = 0; i < dimension_fields.length; i++){
        dimension_data.push({id: dimension_fields[i], text: dimension_fields[i]});
    }
    $("#"+condition_id+" .dimension_condition_select2").select2({data:dimension_data, dropdownAutoWidth:"true"});
    // 删除范围条件
    $("#"+condition_id+" #delete_condition").on("click", function(){
        $(this).parent().remove(); 
    })
}


// 添加一个告警策略
var config_num = 0;
function add_config(){
    config_num += 1;
    // 添加告警策略
    $("#full_config").before("<tr class='tr-a' id='tr-a-"+config_num+"'>"+$("#tr-a-0").html()+"</tr>");
    $("#full_config").before("<tr class='tr-b' id='tr-b-"+config_num+"'>"+$("#tr-b-0").html()+"</tr>");
    var tr_a_id = "#tr-a-"+config_num;
    var tr_b_id = "#tr-b-"+config_num;
    // 初始化 tooltip
    $("[data-toggle='tooltip']").tooltip()
    // 绑定添加告警策略按钮
    $(tr_a_id+" #add_config").on("click", function(){
        add_config();
    })
    // 初始化 select2
    $(tr_a_id+" .conf_select2").select2();
    $(tr_b_id+" .conf_select2").select2();
    // 初始化负责人名单
    $(tr_b_id+' #show_responsible').popover({
        animation: true, //开启淡出的动画效果
        title : '通知名单', //设置标题
        content: "", //设置内容
        delay: {  //显示和隐藏的延迟时间，也可一起设置.例：delay:100
            show: 100,
            hide: 300
        },
        html: true, //是否容许content里包含html代码，默认为false
        placement : 'bottom',  //弹出框出现的位置  top | bottom | left | right | auto
        trigger : 'hover'  //设置弹出框出现的事件  click | hover | focus | manual
    });
    get_cc_role(tr_b_id)
    // 绑定名单展示
    $(tr_b_id +" #role_div").on("click", function(){
        get_cc_role(tr_b_id)
    })
    // 删除告警策略
    $(tr_a_id+" #delete_config").on("click", function(){
        $(this).parent().parent().next().remove(); 
        $(this).parent().parent().remove(); 
        if ($(".config_type").length == 1){
            $("#add_config_default").show();
        }
    })
    // 绑定添加范围条件按钮
    $(tr_a_id+" #add_condition").on("click", function(){
        add_condition(this);
    })
    // 更改策略类型
    $(tr_a_id+" #config_type").on("change", function(){
        $(this).parent().next().children(".config_div").hide();
        $(this).parent().next().children("#config_"+$(this).val()).show();
    })
    // 更改策略 上升/下降
    $(tr_a_id+" .config_symbol_type").on("change", function(){
        $(this).parent().children(".config_symbol").toggle();
    })
    // 使用全局配置
    $(tr_b_id+" #use_full_config").on("change", function(){
        $(this).parent().parent().parent().next().toggle();
        if ($(".use_full_config:checked").length == 0){
            $("#full_config").hide();
        } else {
            $("#full_config").show();
        }
    })
    // 初始化人员选择
	$(tr_b_id+" #member").attr("id", tr_b_id.slice(1, tr_b_id.length)+"member");
	$(tr_b_id+"member").memberInput();
    // 隐藏全局添加按钮
    $("#add_config_default").hide();
    // 显示配置的 tr
    $(tr_a_id).show();
    $(tr_b_id).show();
}
// 绑定全局添加告警策略按钮
$("#add_config_default").on("click", function(){
    add_config();
})


//删除监控配置
$("#delete_monitor").on("click", function(){
    $("#delete_monitor").addClass("king-disabled");
    $.post(site_url+"delete_monitor_config/", {monitor_id: monitor_id}, function (feedback) {
        console.log(feedback);
        $("#delete_monitor").removeClass("king-disabled");
        if (feedback.result){
            if(callback_url == ""){
                app_alert("删除监控成功")
            }
            else{
                window.location.href = callback_url + "?monitor_id=" + feedback.data + "&args=" + callback_args;
            }
        } else {
            app_alert("删除监控失败，请联系管理员："+feedback.message, "fail")
        }
    }, "JSON")
})


//提交操作 operate_type: access 接入; update: 编辑
function save_monitor_config(operate_type, desc){
    param = get_submit_param();
    if (!param){
        console.log("save_config disabled false");
        $("#save_config").attr("disabled", false);
        return
    }
    $.post(site_url+operate_type+"/", {param: JSON.stringify(param)}, function (feedback) {
        console.log(feedback);
        // $("#deploy_btn_save").removeClass("king-disabled");
        // d.close()
        // d.remove()
        if (feedback.result){
            if(callback_url == ""){
                app_alert(desc+"成功")
            }
            else{
                window.location.href = callback_url + "?monitor_id=" + feedback.data + "&args=" + callback_args;
            }
        } else {
            app_alert("新建配置失败，请联系管理员："+feedback.message, "fail")
            $("#save_config").attr("disabled", false);
        }
    }, "JSON")
}


// 初始化数据来源
change_data_src();

// 初始化全局配置
init_full_config();

// 初始化
function init_deploy(){
    // 初始化数据平台数据
    get_result_table();

    // 初始化监控配置表格
    add_config();
}
