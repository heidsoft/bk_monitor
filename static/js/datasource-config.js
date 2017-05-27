// 数据源列表vue对象
var g_ds_form_vue;
var g_options;

// 请求配置项
get_options('field_type|file_frequency|data_encode|sep');

$(document).ready(function(){
    // 监听字段输入，绑定校验事件
    $("#ds_form").on("blur", "input[type='text'], textarea, select, input[type='radio']", validate);

    // 提交表单
    $("#btn_save").click(function(){
        submit_form();

    });

    // 取消
    $("#btn_cancel").click(function(){
        window.location.href = '{0}{1}/datasource/'.format(site_url, cc_biz_id);

    });

    // 隐藏/显示表单
    $('[data-type="panel-collapse"]').on('click', function(){
        var $this = $(this);

        $this.parent().next().slideToggle();
        $this.children('i').toggleClass('expanded');
    });

    // 获取ds_id
    var ds_id;
    try{
        ds_id = /config\/(\d+)/.exec(window.location.pathname)[1];
    }
    catch (err) {
        ds_id = '0';
    }
    // 创建vue对象
    g_ds_form_vue = init_ds_form_vue(ds_id);

    if(ds_id!='0'){
        // 请求数据
        get_form_data();
    }
});


function ajax_get(url, params, callback) {
    $.get(url, params, callback, 'json');
}


function ajax_post(url, params, callback) {
    $.post(url, params, callback, 'json');
}


function get_options(config_name){
    ajax_get('{0}{1}/datasource/get_options/?config_name={2}'.format(site_url, cc_biz_id, config_name), {}, render_options);
}

function get_form_data(){
    // 显示loading
    $('#ds_form div.loading').removeClass('hide');
    ajax_get(window.location.href.replace('config', 'get_ds'), {}, render_form_data);
}


function render_options(res) {
	if(res.result){
        if(g_ds_form_vue==undefined){
            g_options = res.data;
        } else{
            g_ds_form_vue.options = res.data;
        }
	} else{
		alert_topbar("请求配置选项失败：" + res.message, "fail");
	}
}


function render_form_data(res) {
    // 隐藏loading
    $('#ds_form div.loading').addClass('hide');
	if(res.result){
        var ds_data = JSON.parse(res.data.data_json);
        ds_data.ips = ds_data.ips.join('\n');
        update_dict(g_ds_form_vue.ds_data, ds_data);
	} else{
		alert_topbar("请求数据失败：" + res.message, "fail");
	}
}


function update_dict(src, target){
    for(key in target){
        src[key] = target[key];
    }
}


function init_ds_form_vue(ds_id) {
    return new Vue({
        el: '#ds_form',
        data: {
            ds_id: ds_id,
            ds_data: {
                data_set: '',       // 数据表名
                data_desc: '',      // 中文名称
                ips: [],            // 采集对象IP列表
                log_path: '',       // 日志路径
                file_frequency: '',      // 日志生成频率
                data_encode: '',    // 字符编码
                sep: '',           // 数据分隔符
                conditions: [],     // 采集范围
                fields: [get_default_field_data()]         // 数据表字段
            },
            // 字段时间格式和时区
            time_format: '1',
            time_zone: '+8',
            // 下拉框选项
            options: g_options
        },
        computed: {

        },
        methods: {
            add_condition: function(index) {
              this.ds_data.conditions.splice(index + 1, 0, {
                op: '',
                value: ''
              });
            },
            remove_condition: function(index) {
              this.ds_data.conditions.splice(index, 1);
            },
            add_field: function(index) {
              this.ds_data.fields.splice(index + 1, 0, get_default_field_data());
            },
            remove_field: function(index) {
              this.ds_data.fields.splice(index, 1);
            },
            set_time_field: function(index) {
                var fields = this.ds_data.fields;
                for(var i=0; i<this.ds_data.fields.length; ++i){
                    fields[i].time_format = '';
                    fields[i].time_zone = '';
                }
                fields[index].time_format = this.time_format;
                fields[index].time_zone = this.time_zone;
            }
        }
    });
}


function get_default_field_data(){
    return {
        name: '',
        description: '',
        alis: '',
        type: '',
        time_format: '',
        time_zone: ''
    };
}


// 校验的入口函数
function validate(){
    var $target = $(this);
    // 校验
    var ret = validate_switch($target);
    // 更新错误提示
    update_feedback($target, ret);
    return !ret.result;
}


// 校验每个字段
function validate_switch($target){
    var name = $target.attr("name");
    var val = $.trim($target.val());
    var ret = {result: true, msg: "", position: 'right'};
    switch (name){
        // 数据表名
        case 'data_set':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入数据源表名";
            }
            else {
                var reg = /^[a-zA-Z][a-zA-Z0-9_]*$/;
                if(!reg.test(val)){
                    ret.result = false;
                    ret.msg = "表名不合法，请遵循MySQL的数据表命名规则";
                }
            }
            break;
        case 'data_desc':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入数据源的中文名称";
            }
            break;
        case 'ips':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入采集对象";
            }
            else {
                var ips = val.split('\n');
                var reg = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
                var error_ips = ips.filter(function(ip){
                    return !reg.test(ip);
                });
                if(error_ips.length>0){
                    ret.result = false;
                    ret.msg = "请输入合法的IP:  {0}".format(error_ips.join('; '));
                }
            }
            break;
        case 'log_path':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入日志路径";
            }
            break;
        case 'file_frequency':
            if(val==''){
                ret.result = false;
                ret.msg = "请选择日志生成频率";
            }
            break;
        case 'data_encode':
            if(val==''){
                ret.result = false;
                ret.msg = "请选择字符编码";
            }
            break;
        case 'sep':
            if(val==''){
                ret.result = false;
                ret.msg = "请选择数据分隔符";
            }
            break;
        case 'condition_index':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入列值";
            }
            else{
                var reg = /^[0-9]*$/;
                if(!reg.test(val)){
                    ret.result = false;
                    ret.msg = "列值只能是数字，请输入正确的列值";
                }
            }
            break;
        case 'condition_value':
            if(val==''){
                ret.result = false;
                ret.msg = "请输入条件值";
            }
            break;
        case 'field_name':
            ret.position = 'top';
            if(val==''){
                ret.result = false;
                ret.msg = "请输入字段名";
            }
            else{
                var reg = /^[a-zA-Z][a-zA-Z0-9_]*$/;
                if(!reg.test(val)){
                    ret.result = false;
                    ret.msg = "请输入合法的字段名";
                }
                else if(search_field_name(val)>1){
                    ret.result = false;
                    ret.msg = "不能和其他字段名或别名有重复";
                }
            }
            break;
        case 'field_description':
            ret.position = 'top';
            if(val==''){
                ret.result = false;
                ret.msg = "请输入字段的中文描述";
            }
            break;
        case 'field_alis':
            ret.position = 'top';
            if(val!=''){
                var reg = /^[a-zA-Z][a-zA-Z0-9_]*$/;
                if(!reg.test(val)){
                    ret.result = false;
                    ret.msg = "请输入合法的别名";
                }
                else if(search_field_name(val)>1){
                    ret.result = false;
                    ret.msg = "不能和字段名或其他别名有重复";
                }
            }
            break;
        case 'field_type':
            ret.position = 'top';
            if(val==''){
                ret.result = false;
                ret.msg = "请选择字段类型";
            }
            break;
        case 'field_time':
            // 特殊处理，选中后隐藏错误提示
            $("input[name='field_time']").next(".error-tips").remove();
            break;
        default:
            console.log(name+ " validator is not exist.");
            break;
    }
    return ret;
}


function search_field_name(field_name){
    var count = 0;
    g_ds_form_vue.ds_data.fields.map(function(field){
        // 字段名和别名不能重复
        if(field.name==field_name) {
            ++count;
        }
        if(field.alis==field_name){
            ++count;
        }
    });
    return count;
}


function search_field_time(){
    var count = 0;
    g_ds_form_vue.ds_data.fields.map(function(field){
        // 字段名和别名不能重复
        if(field.time_format!='' && field.time_zone!='') {
            ++count;
        }
    });
    return count;
}


// 更新错误提示
function update_feedback($target, ret){
    $target.next('.input-tips, .error-tips').remove();
    if(!ret.result){
        $target.after(build_error_msg(ret.position, ret.msg));
        //$target.focus();
        $target.addClass('error');
    } else{
        $target.removeClass('error');
    }
}


function build_error_msg(position, msg){
    switch(position){
        case 'top':
            return '<div class="error-tips">{0}</div>'.format(msg);
        case 'right':
            return '<span class="input-tips error"><i class="fa fa-times-circle"></i>{0}</span>'.format(msg);
        default:
            return '';
    }
}


// 保存
function submit_form(){
    // 校验输入内容
    var errors = $("#ds_form").find("input[type='text'], textarea, select, input[type='radio']").filter(validate);

    // 时间字段有且仅有一个
    if(search_field_time()!=1){
        var $target = $($("input[name='field_time']")[0]);
        update_feedback($target, {result: false, msg: "请选择时间字段", position: "top"});
        errors.push($target);
    }

    if(errors.length==0){
        dialog({
            width: 260,
            title: "提示",
            content: "确定提交吗？",
            okValue: "确定",
            ok: function () {
                // 显示loading
                $('#ds_form div.loading').html(set_loading_content('正在处理，请稍候...'));
                $('#ds_form div.loading').removeClass('hide');
                ajax_post(window.location.href, {"datasource_data": JSON.stringify(g_ds_form_vue.ds_data)}, submit_form_callback);
            },
            cancelValue: "取消",
            cancel: function () {

            }
        }).show();
    }
    else{
        // 输入焦点定位到第一个错误项
        errors[0].focus();
    }
}


function submit_form_callback(res) {
    // 隐藏loading
    $('#ds_form div.loading').addClass('hide');
	if(res.result){
        alert_topbar("提交成功，正在跳转到首页...", "success");
        window.location.href = '{0}{1}/datasource/'.format(site_url, cc_biz_id);
	} else{
		alert_topbar("请求数据失败：" + res.message, "fail");
	}
}


function set_loading_content(msg){
    var content = '<div class="loading-wrapper">' +
        '<img alt="loadding" src="'+static_url+'img/hourglass_36.gif">' +
        '{0}</div>';
    return content.format(msg);
}