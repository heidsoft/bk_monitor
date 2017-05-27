var monitor_field_list_info = {};
var host_index_list = [];
var monitor_list = [];
var shield_set_selector = $("#shield_set_selector");
var shield_mod_selector = $("#shield_module_selector");
var shield_id = -1;
var shield_info = {
    monitor_field_list: [],
    hours_delay: 1
};
var strategy_list = [];
var strategy_selector = $("#strategy_selector");


	function shield_initPlugins(){
        // config.js中已处理
		//$('[data-type="icheck"]').iCheck({
		//    checkboxClass: 'icheckbox_minimal-blue',
		//    radioClass: 'iradio_minimal-blue',
		//    increaseArea: '20%' // optional
		//});
        strategy_selector.select2({
            data: strategy_list,
            placeholder: '请选择屏蔽对象.'
        });

		//日期选择器(Bootstrap)-2，日期选择
	    $('#newDate').datetimepicker({
	        language:  'zh-CN',
	        weekStart: 1,
	        todayBtn:  true,
	        autoclose: true,
	        todayHighlight: true,
	        startView: 2,
	        minView: 0,
	        forceParse: false,
	        format:"yyyy-mm-dd hh:ii",
            startDate: moment().format('YYYY-MM-DD HH:mm:ss'),
            endDate: moment().add(7,"d").format('YYYY-MM-DD HH:mm:ss'),

	    });
	}

	function shield_bindEvents(){

		//关闭侧边栏
		$('#close, #sideContent').on('click', function(event){
            if($(event.target).attr('data-type') == 'close') {
                close_shield_side();
            }
		});

		//radio切换
		$('[data-group="top"]').on('ifChecked', function(){
            if ($(this).attr("name") == "alert_type"){
                $("#monitor_target").select2("val", "").trigger("change");
                refresh_monitor_target_selector();
            }
			var group = $('[data-group="top"]');
				checked = '';

			[].forEach.call(group, function(cur, index, arr){
				if(cur.checked){
					checked += $(cur).attr('data-value') + ' ';					
				}
			});

			if(checked.indexOf('monitor_ip') > -1){
				$('#allMainFrames').removeClass('hidden').siblings('[data-type="sub"]').addClass('hidden');
			}
			else if(checked.indexOf('monitor_set') > -1){
				if(checked.indexOf('mainframeMonitor') > -1){
					$('#mainframeSet').removeClass('hidden').siblings('[data-type="sub"]').addClass('hidden');
				}
				else if(checked.indexOf('customMonitor') > -1){
					$('#customSet').removeClass('hidden').siblings('[data-type="sub"]').addClass('hidden');
				}
			}
            if (checked.indexOf('customMonitor') > -1){
                $(".condition_label").addClass("hidden");
                $("[data-value=monitor_set]").iCheck("check");
            }
            if (checked.indexOf('mainframeMonitor') > -1){
                $(".condition_label").removeClass("hidden");
            }
		});

		//删除
		$(document).on('click', '[data-type="delete"]', function(){
			var $this = $(this);
            if ($("[name=shield_monitor_field]").length == 1){
                $this.parents('.subcontent-row').find("[name=shield_monitor_field]").select2("val", "");
                $this.parents('.subcontent-row').find("[name=shield_monitor_field_value]").val("");
                return
            }
            $this.parents('.subcontent-row').remove();
		});

		//新增
		$(document).on('click', '[data-type="add"]', function(){
			var html = '<div class="subcontent-row">'+
							'<input style="width:200px" name="shield_monitor_field">'+
                            '<span class="pre-span">包含</span>'+
						    '<input type="text" name="shield_monitor_field_value" id="andField" class="alert__input" placeholder="多个值使用,分隔">'+
						    '<span class="operator-row">'+
							    '<span class="new-operator" data-type="add">'+
							    	'<i class="fa fa-plus-circle new-add"></i>'+
							    '</span>'+
							    '<span class="new-operator" data-type="delete">'+
							    	'<i class="fa fa-minus-circle new-delete"></i>'+
							    '</span>'+
						   	'</span>'+
						'</div>';
			var $html = $(html);
			$('.subcontent-row:last').after($html);
			initNewRow();
		});

		//切换屏蔽事件中的日期选择
		$('[name="auto_process_method"]').on('click', function(){
			var $this = $(this),
				id = $this.attr('id'),
				date = $('#newDate');

			if(id == 'customTime' && date.hasClass('hidden')){
				date.removeClass('hidden');
			}
			else if(id != 'customTime'){
				date.addClass('hidden');
			}
		});
	}

	shield_initPlugins();
	initNewRow();
	shield_bindEvents();
    refresh_monitor_target_selector();
    init_shield_set_selector();

function init_strategy_selector(monitor_id){
    $.get(site_url+cc_biz_id+'/'+'get_alarmdef_by_monitor_id/', {monitor_id: monitor_id}, function(res){
        strategy_selector.select2({
            data: res.data,
            placeholder: '请选择策略.'
        }).select2("val", shield_info.alarm_source_id?shield_info.alarm_source_id:"0")
    }, 'json')
}

function initNewRow(){
    var monitor_id = $("#monitor_target").val();
    if (!monitor_id){
        $('[name=shield_monitor_field]').select2({
            data: [],
            placeholder: '请选择屏蔽对象.'
        });
    }else{
        var monitor_field_list = monitor_field_list_info[monitor_id];
        if (!monitor_field_list){
            // get field list
            $.ajax({
                url: site_url+cc_biz_id+'/'+'list_custom_monitor_field/',
                data: {"monitor_id": monitor_id},
                type: "GET",
                dataType: "json",
                success: function (resp) {
                    if (resp.result) {
                        $('[name=shield_monitor_field]').select2({
                            data: resp.data,
                            placeholder: "请选择字段",
                            language: "zh-CN"
                        });
                        monitor_field_list_info[monitor_id] = resp.data;
                    }
                }
            });
        }else{
            // make options
            $('[name=shield_monitor_field]').select2({
                data: monitor_field_list_info[monitor_id],
                placeholder: "请选择字段",
                language: "zh-CN"
            });
        }
    }
}

function edit_shield(_shield_id){
    shield_id = _shield_id;
    open_shield_side();
    $("#shield_action").text(shield_id == -1?"新增告警屏蔽":"编辑告警屏蔽");
    if (shield_id != -1){
        $.ajax({
            url: site_url+cc_biz_id+'/'+'shield_info/',
            data: {"shield_id": shield_id},
            type: "GET",
            dataType: "json",
            success: function (resp) {
                if (resp.result) {
                    shield_info = resp.data;
                    init_page_by_shield_info(shield_info);
                }
            }
        });
    }else{
        shield_info = {
            monitor_field_list: [],
            hours_delay: 1
        }
        init_page_by_shield_info(shield_info);
    }
}

function init_page_by_shield_info(shield_info){
    $("[name=shield_desc]").val(shield_info.shield_desc);
    $("[name=alert_type][value="+shield_info.alarm_type+"]").iCheck("check");
    $("[name=shield_perform_cate][value="+shield_info.perform_cate+"]").iCheck("check");
    $("#monitor_target").select2("val", shield_info.monitor_target).trigger("change");
    $("input[name=auto_process_method][value="+shield_info.hours_delay+"]").prop("checked", true).trigger("click");
    $("#newDate").find("input").val(shield_info.end_time);

    shield_set_selector.select2("val", shield_info.set).trigger("change");
    shield_mod_selector.select2("val", shield_info.mod);
    $("#shield_ip").val(shield_info.ip);
    // 屏蔽范围使用策略替换
    //if ($("[name=shield_monitor_field]").length >1){
    //    $("[name=shield_monitor_field]").each(function(i){
    //        if (i!=0){
    //            $(this).closest(".subcontent-row").remove();
    //        }
    //    })
    //}
    //for (var i = 0; i<shield_info.monitor_field_list.length; i++){
    //    if (i>0){
    //        $($("[name=shield_monitor_field]")[i-1]).closest(".subcontent-row").find("[data-type=add]").click()
    //    }
    //    $($("[name=shield_monitor_field]")[i]).select2("val", shield_info.monitor_field_list[i][0])
    //    $($("[name=shield_monitor_field]")[i]).val(shield_info.monitor_field_list[i][0]);
    //    $($("[name=shield_monitor_field]")[i]).closest(".subcontent-row").find("[name=shield_monitor_field_value]").val(shield_info.monitor_field_list[i][1])
    //}

}

function update_shield(obj){
    shield_id = $(obj).attr("shieldid")
    edit_shield(shield_id)
}

function open_shield_side(){
    var sideContent = $('#shield_side');
    sideContent.removeClass('hidden');
    getComputedStyle(document.querySelector('body')).display;
    sideContent.find('#close').addClass('open');
    sideContent.find('.shield-edit').addClass('open');
    sideContent.find('#shield-detail').removeClass('hidden');

    $('article.shield-content').css('overflow', 'hidden');
}

function close_shield_side(){
    var sideContent = $('#shield_side');
    sideContent.find('.shield-edit').removeClass('open').children('#shield-detail').addClass('hidden');
    sideContent.find('#close').removeClass('open');
    setTimeout(function(){
        sideContent.addClass('hidden');
        $('article.shield-content').css('overflow', 'auto');
    }, 300);

}

function get_alert_type(){
    return $("[name=alert_type]:checked").val();
}

function refresh_monitor_target_selector(){
    if (get_alert_type()=="performance"){
        if (host_index_list.length == 0){
            $.get(site_url + cc_biz_id + '/'+'bp/host_index_option_list/', {}, function(res){
                if (res.result){
                    host_index_list = res.data;
                    if (host_index_list.length==0){return}
                    refresh_monitor_target_selector();
                }else{
                    host_index_list = [];
                }
            }, "json");
        }else{
            $("#monitor_target").select2({
                data: host_index_list,
                placeholder: "请选择指标",
                language: "zh-CN"
            });
            if (shield_info.alarm_type == "performance"){
                $("#monitor_target").select2("val", shield_info.monitor_target).trigger("change");
            }
        }
    }
    if (get_alert_type()=="custom"){
        if (monitor_list.length == 0){
            $("#monitor_target").select2({
                data: monitor_list,
                placeholder: "加载中...",
                language: "zh-CN"
            });
            $.get(site_url + cc_biz_id + '/'+'custom_monitor_option_list/', {}, function(res){
                if (res.result){
                    monitor_list = res.data;
                    $("#monitor_target").select2({
                        data: monitor_list,
                        placeholder: "请选择屏蔽对象",
                        language: "zh-CN"
                    });
                    if (monitor_list.length == 0){return}
                    refresh_monitor_target_selector();
                }else{
                    monitor_list = [];
                }
            }, "json");
        }else{
            $("#monitor_target").select2({
                data: monitor_list,
                placeholder: "请选择屏蔽对象",
                language: "zh-CN"
            }).off('change').change(function(e){
                if ($("input[name=alert_type]:checked").val()=="custom"){
                    init_strategy_selector($(e.target).select2("val"));
                }
            });
            if (shield_info.alarm_type == "custom"){
                $("#monitor_target").select2("val", shield_info.monitor_target).trigger("change");
            }
        }
    }
}

function init_shield_set_selector(){
    // 拉取集群列表
    $.getJSON(site_url+cc_biz_id+'/'+'get_cc_set/', function (resp) {
        if (resp.result) {
            shield_set_selector.select2({
                data: resp.data,
                placeholder: "请选择集群",
                language: "zh-CN"
            }).change(function (e) {
                // 集群选择触发事件
                // 查找SET下的模块
                if (!shield_set_selector.select2("data")){
                    return
                }
                var set_id = shield_set_selector.select2("data").id;
                refresh_shield_mods_info(set_id);
            });
            // 主动触发下一级
            shield_set_selector.select2("val", "0").trigger('change');
        }
    });
}

function refresh_shield_mods_info(set_id){
    shield_mod_selector.val("").select2({
        data: [],
        placeholder: "加载中...",
        language: "zh-CN"
    });
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_cc_module/',
        data: {"set_id": set_id},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                shield_mod_selector.select2({
                    data: resp.data,
                    placeholder: "请选择模块",
                    language: "zh-CN"
                });
                shield_mod_selector.select2("val", shield_info.mod?shield_info.mod:"0")
            }
        }
    });
}

$("#shield_side").find("#cancel").click(function(){
    close_shield_side();
});

$("#shield_side").find("#save").click(function(){
    save_shield();
});

function save_shield(){
    if (!check_shield_params()){
        return
    }
    make_saving_button($("#shield_side #save"));
    var params = {
        hours_delay: $("input[name=auto_process_method]:checked").val(),
        biz_id: cc_biz_id,
        shield_desc: $("[name=shield_desc]").val(),
        shield_id: shield_id,
        alert_type: get_alert_type(),
        shield_time: shield_time_list(),
        dimension_list: shield_dimension_list(),
        alarm_source_id: strategy_selector.select2("val"),
        perform_cate: $("[name=shield_perform_cate]:checked").val(),
        ip: $("#shield_ip").val(),
        cc_set: shield_set_selector.select2("val"),
        cc_module: shield_mod_selector.select2("val"),

    };
    if (get_alert_type() == "custom"){
        params["monitor_id"] = $("#monitor_target").val()
    }
    if (get_alert_type() == "performance"){
        params["monitor_target"] = $("#monitor_target").val()
    }
    $.ajax({
        url: site_url+cc_biz_id+'/access_shield/',
        data: {param: JSON.stringify(params)},
        type: "POST",
        dataType: "json",
        success: function (resp) {
            make_saved_button($("#shield_side #save"));
            if (resp.result) {
                alert_topbar("保存成功", "success");
                close_shield_side();
                $("#shield_table_loading").removeClass("hidden");
                location.href = site_url + cc_biz_id + '/config/?tab=shield';
            }else{
                alert_topbar(resp.message, "fail");
            }
        }
    });
}

function shield_dimension_list(){
    var dimension_list = [];
    $("[name=shield_monitor_field]").each(function(index)
    {
        var tr = $($("[name=shield_monitor_field]")[index]).closest(".subcontent-row");
        var field = tr.find("[name=shield_monitor_field]").select2("val");
        var value = tr.find("[name=shield_monitor_field_value]").val();
        if (field && value){
            dimension_list.push({
                field: field,
                value: value
            })
        }
    });
    return dimension_list;
}

function shield_time_list(){
    var hours_delay = $("input[name=auto_process_method]:checked").val();
    var start_time = moment().format('YYYY-MM-DD HH:mm:ss')
    if (hours_delay == 0){
        var end_time = $("#newDate").find("input").val();
        if (!end_time){
            $("#custom_date_error_span").text("请选择时间");
            $("#newDate").find("input").change(function(){
                $("#custom_date_error_span").text("");
            })
        }else{
            if (end_time.split(":").length == 2){
                end_time = end_time + ":00"
            }

        }
    }else{
        end_time = moment().add(hours_delay, 'hours').format('YYYY-MM-DD HH:mm:ss')
    }
    return start_time+"~"+end_time
}

function check_shield_params(){
    // 校验参数
    //if (!$("[name=shield_desc]").val()){
    //    $("#shield_desc_error_span").text("请填写告警描述");
    //    $("[name=shield_desc]").unbind("click").click(function(){
    //        $("#shield_desc_error_span").text("")
    //    });
    //    return
    //}
    if (!$("#monitor_target").select2("val")){
        $("#monitor_target_error_span").text("请选择屏蔽对象");
        $("#monitor_target").on("select2-opening", function(){
            $("#monitor_target_error_span").text("");
        });
        return false
    }
    if ($("[name=shield_perform_cate]:checked").val()=="ip"){
        var new_ip_list = [];
        var ip_rex = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
        var ip_list = $("#shield_ip").val().split(",");
        for (var i= 0,len=ip_list.length;i<len;i++){
            var ip = ip_list[i].trim();
            if (ip.match(ip_rex)){
                new_ip_list.push(ip)
            }
        }
        $("#shield_ip").val(new_ip_list.join(","));
    }
    return true
}

function make_saving_button(button){
    button.attr("disabled", true);
    button.html('保存中...')
}

function make_saved_button(button){
    button.attr("disabled", false);
    button.html('保存')
}