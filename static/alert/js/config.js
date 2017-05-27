//监控配置相关的js

// 判断是否为整数
function isInteger(obj) {
    return (obj | 0) === obj
}
// 返回按钮事件
$("#back_btn_id").click(function(){
	if($(this).attr("disabled")){
		return false;
	}
	var obj = $(this);
	var is_alarm_strategy_edit = $("#is_alarm_strategy_edit").val();
	//if(is_alarm_strategy_edit == '1'){
	//	$(obj).attr("disabled", true);
	//	var msg = "您已经操作过【告警策略】<br><br>是否确定离开？<br><br>确定后页面上所有的操作都不会保存！";
	//	_app_confirm(msg, function(){
	//		$(obj).attr("disabled", false);
	//		close_div(iframeCallBack(''));
	//	}, function(){
	//		$(obj).attr("disabled", false);
	//	})
	//}else{
    close_div(iframeCallBack(''));
	//}
})
// 取消按钮绑定事件
$("#cancel_config").click(function(){
	$("#back_btn_id").click();
})
/****************** 参数验证 start *************************/
// 监控名称检查
function _check_monitor_name(){
  var re_name = false;
  var old_name = $("#old_monitor_name").val();
  var is_scene = $("#is_scene").val();
  //场景页面不检查监控名称
  if(is_scene == '1'){
	  return true;
  }
  $.ajax({
    type: 'GET',
    url:  site_url + cc_biz_id +'/config/check_monitor_name/',
    data: {'name': $.trim($('#monitor_name').val()), 'old_name': old_name},
    success: function(d){
      if(d.result){
        re_name = true
      }else{
        $('#tip_monitor_name').html(d.message);
        $('#tip_monitor_name').parents('.form-group').addClass('has-error');
        re_name = false;
      }
    },
    dataType: 'json',
    async: false,
  });
  return re_name;
}

function check_monitor_name(){
    var flag = true;
    if($.trim($("#monitor_name").val()) == ''){
      $('#tip_monitor_name').html('请填写监控名称');
      $('#tip_monitor_name').parents('.form-group').addClass('has-error');
      flag = false;
    }else{
      var return_re = _check_monitor_name();
      flag = return_re;
      if(return_re){
        $('#tip_monitor_name').html('');
        $('#tip_monitor_name').parents('.form-group').removeClass('has-error');
      }
    }
    return flag;
}

function chek_base_config_parm(){
 	$("#tip_config").text('');
 	flag = true;
 	
 	// 验证监控名称
    if(scenario != "performance" && scenario != "basic"){
        flag = check_monitor_name();
        if(!flag){return false;}
    }
    
    console.log('not_empty');
 	// 验证参数
 	$(".not_empty").each(function(){
 		res = check_not_empty_element($(this));
        console.log($(this))
 		if(!res){
 			flag = false;
 			return false;
 		}
 	})
 	if(!flag){return false;}
 	
 	// TODO selet2 选择值判断
 	 console.log('not_empty_select');
 	$(".form-group:visible input.not_empty_select").each(function(){
 		 res = check_not_empty_select_element($(this));
 		 if(!res){
 			 flag = false;
 			 return false;
 		 }
 	 })
 	 if(!flag){return false;}
 	
 	// 弹出层输入值判断
 	console.log('some-input');
 	$(".some-label:visible .some-input").each(function(){
 		var cur_val = $(this).val();
 		if(!cur_val){
 			$(this).parents('.some-label').click();
 			$(this).siblings("span").css({"display":"inline-block"});
 			console.log(this +",必填");
 			flag=false;
 			return false;
 		}
 	})
 	if(!flag){return false;}
 	
 	console.log('condition_fileds');
 	try{
 		var condition_fileds = get_condition_fileds();
 		var condition_filed_ids = [];
 		for(con in condition_fileds){
 			condition_filed_ids .push(condition_fileds[con].id);
 		}
 		// 监控策略中，筛选条件判断
 		$('.condition_fields').each(function(){
 			var cur_text = $.trim($(this).text())
 			var cur_fields = cur_text ? cur_text.split(',') : [];
 			if(cur_fields){
 				for(i in cur_fields){
 					console.log(cur_fields[i])
 					console.log(condition_filed_ids)
 					if( $.inArray(cur_fields[i], condition_filed_ids) < 0 ){
 						$("#tip_config").text("下面告警策略中的筛选条件["+cur_fields[i]+"]不生效");
 						$(this).parents('tr').css('background-color', 'darksalmon');
 						flag=false;
 			 			return false;
 					} 
 				}
 			}
 		})
 	}catch(e){
 		console.log(e);
 	}
 	if(!flag){return false;}
 	
 	 // 监控策略判断
 	 //var tbody = $("#strategy_table tbody");
 	 //var tr_len = $(tbody).find('tr').length;
 	 //if(tr_len <= 1){
 	 //	var td_len = $(tbody).find('tr').eq(0).find('td').length;
 	 //	if(td_len <=1 ){
 	 //		$("#tip_config").text('请添加告警策略');
 	 //		return false;
 	 //	}
 	 //}
 	 return true;
}
//验证不为空的元素
function check_not_empty_select_element(obj){
	var flag = true;
	var cur_id = $(obj).attr('id');
	var cur_val = $.trim($(obj).val());
	console.log('id:'+cur_id);
	console.log('var:'+cur_val);
	if(cur_val == ''){
		$("#tip_"+cur_id).html('必填');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		console.log("#tip_"+cur_id +",必填");
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
}
// 验证不为空的元素
function check_not_empty_element(obj){
	var flag = true;
	var cur_val = $.trim($(obj).val());
	var cur_id = $(obj).attr('id');
	if(cur_val == ''){
		$("#tip_"+cur_id).html('必填');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		console.log("#tip_"+cur_id +",必填");
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
}
// 验证数字元素
function check_number_element(obj){
	var flag = true;
	var cur_val = $.trim($(obj).val());
	var cur_id = $(obj).attr('id');
	var cur_name = $(obj).attr('name');
	if(cur_val == '' || isInteger(cur_val) ){
		$("#tip_"+cur_id).html('请输入一个整数');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
}

//绑定监控字段的变动
$("#monitor_field").on("change", function(){
    $("#count_method").select2("readonly", false);
    if ($(this).val() == "*"){
        $("#count_method").append('<option value="count">COUNT</option>');
        var monitor_field_name = "*";
        $("#count_method").select2("val", "count").trigger("change");
        $("#count_method").select2("readonly", true);
    } else {
        $("#count_method").select2("val", "sum")
        $("#count_method option[value=count]").remove();
        var monitor_field_name = $("#monitor_field").select2("data").text;
    }
    $("#monitor_field_show").html(monitor_field_name);
})
// 场景监控指标绑定统计方式
$(".count_select:visible").on("change", function(){
	var cur_val = $(this).val();
	var cur_id = $(this).attr('id');
	if(cur_val){
		// 监控指标为count时，统计方式为 COUNT, 此外为 SUM
		if(cur_val == '*'){
			$("#"+cur_id+"_method").select2("val", "count").trigger("change");
		}else{
			$("#"+cur_id+"_method").select2("val", "sum").trigger("change");
		}
		$("#"+cur_id+"_method").select2("readonly", true);
	}else{
		// 监控指标为空时，统计方式可选
		$("#"+cur_id+"_method").select2("readonly", false);
	}
})
/****************** 参数验证 end   *************************/
function submit_strategy_data(param, alram_strategy_id, is_auto){
    var url = site_url + cc_biz_id +'/config/strategy_save/'+alram_strategy_id+'/';
    var s_id = $.trim($("#s_id").val());
    var _this = $;
    $.post(url,{
    	's_id': s_id,
    	'param': JSON.stringify(param)
    }, function(feedback){
    	$("#submit_stragegy").html('确定');
    	if (feedback.result){
    		$("#tip_config").text('');
    		if(!is_auto){
        		// 记录告警策略操作动作(自动保存时不记录)
        		$("#is_alarm_strategy_edit").val('1');
    			var d = dialog({id: 'add_alarm_strategy'});
    			d.close().remove();
    		}
    		// 刷新列表数据
    		get_strategy('');
    	}else{
    		if(!is_auto){
    			// 提示错误信息
    			$("#tip_all").text(feedback.message);
    			$("#submit_stragegy").attr("disabled", false);
    		}
    	}
    }, 'json');
}
/*
 * param solution_id: 自愈套餐id
 */
function add_default_strategy(monitor_level, strategy_id, solution_id){
	var param = {
        "monitor_level": "1", 
        "perform": {}, 
        "strategy_id": "8", 
        "rules": {"converge_count": "1", "converge_period": "5"}, 
        "strategy_option": {}, 
        "monitor_config": {
            "responsible": "", 
            "solution_id": "", 
            "notify": {"notify_way": ["mail", "wechat"], "role_list": ["Maintainers"]}
        }, 
        "condition": []
    };
	param['scenario'] = scenario;
	param['monitor_level'] = monitor_level;
	param['strategy_id'] = strategy_id;
	param['monitor_config']['solution_id'] = solution_id;
    if(strategy_id == 99){
        param["strategy_option"] = {"continuous": 5}
    }
	try{
		submit_strategy_data(param, 0, true);
	}catch(e){
		console.log(e);
	}
}

/*
 * 通过数据平台官网App添加数据表
 * note: 只支持在正式环境蓝鲸平台中调用
 */ 
function add_data_table_by_app(){
	// 数据平台 app_code
	var target_app_code = 'data';
	// 数据接入连接
	var target_url = '/dataset/couplein/?from=ja&cc_biz_id='+cc_biz_id;
	try{
		Bk_api.open_other_app(target_app_code, target_url);
	}catch(e){
		var msg = '请在蓝鲸平台中打开该应用';
		// 提示用户必须在蓝鲸平台中打开
	    dialog({
	        width: 430,
	        title: '提示',
	        ok: function() {
	        	// 在蓝鲸平台中打开该应用
	        	window.top.location.href = 'http://o.qcloud.com/console/?app=alert';
	        },
	        okValue: '跳转到蓝鲸平台',
	        cancelValue: '取消',
	        cancel: function (){},
	        content: '<div class="king-notice-box king-notice-warning"><p class="king-notice-text">'+msg+'</p></div>'
	    }).show();
	}	
}

/*
 * 刷新数据源，提供给 数据平台官网调用
 * param result_table_id:数据平台官网返回的 table_id
 */
function refresh_data_table(result_table_id){
	// 刷新数据源
	try{
		get_result_table();
	}catch(e){
		console.log(e);
		get_dataset("all");
	}
	// 选中新添加的数据
	$("#data_table").select2("val", result_table_id);
	// 并操作页面上相应元素
	try{
		change_data_table();
	}catch(e){
		console.log(e);
	}
}

/*
 * 只获取dataset, 供场景接入调用获取数据源
 */
function get_dataset(srctype){
    var group_data = [];
    $.ajax({
        url: site_url+"api/trt/list_datasets/",
        dataType: "json",
        data: {
            biz_id: cc_biz_id,
            set_type: "biz",
        },
        success: function(result){
            if (result.result){
                var data = [];
                $.each(result.data, function (index, value) {
                    if (value["data_desc"]){
                        var text = "【" + value["data_id"] + "】" + value["data_set"] + "(" + value["data_desc"] + ")";
                    } else {
                        var text = "【" + value["data_id"] + "】" + value["data_set"]
                    }
                    if(srctype == "all" || srctype == value["data_src_item"]){
                        data.push({
                            "id": value["data_id"],
                            "type": "dataset",
                            "text": text,
                            "dataset": value["data_set"],
                            "data_format": value["data_format_id"],
                        });
                    }
                })
            }
            else {
                var data = [{"id": "", "text": "获取源数据失败:"+result.message}]
            }
            if(data.length > 0){
                group_data.push({"text":"源数据", "children":data});
            }else{
                group_data.push({"text":"无数据", "children":data});
            }
            $("#data_table").select2({data:group_data, dropdownAutoWidth:"true"});
            $("#data_table_loadding").hide();
    	},
    })
}

function change_type_select(type){
	if(type=='mobile'){
        $("input[name=biz_type][value=mobile]").attr("checked", "checked");
        if(scenario == "online"){
            $("#num_rules").select2("val", "os");
        }
        else{
            $("#num_rules").select2("val", "single");
        }
        $("#biz_type_radio").trigger("change");
	}else{
        $("input[name=biz_type][value=pc]").attr("checked", "checked");
        $("#biz_type_radio").trigger("change");
	}
}

function game_type_select(){
    $.get(site_url+"api/trt/is_mobile_game/", {cc_biz_id: cc_biz_id}, function (feedback) {
        if (feedback.result){
        	if(feedback.data){
        		var type = 'mobile';
        	}else{
        		var type = 'pc'
        	}
        	change_type_select(type);	
            //手游
//            if(feedback.data){
//                $("input[name=biz_type][value=mobile]").attr("checked", "checked")
//                if(scenario == "online"){
//                    $("#num_rules").select2("val", "os")
//                }
//                else{
//                    $("#num_rules").select2("val", "single")
//                }
//                $("#biz_type_radio").trigger("change")
//            } else {
//                $("input[name=biz_type][value=pc]").attr("checked", "checked")
//                $("#biz_type_radio").trigger("change")
//            }
        }
    }, "JSON")
}

/*
 * 初始化数据平台数据数据源的监控配置
 * param: 
 *	field_list 初始化字段列表: id: select id; type:value/dimension/ccset; is_multiple: true/false
 * 	exp field_list: {["id": ios_field, "type": "value", "is_multiple": false]}
 */
function show_field_by_dataset(field_list){
    if ($("#data_table").val()== ''){ return }
    $.ajax({
        url: site_url+"api/trt/list_dataset_fields/",
        dataType: "json",
        data: {
            data_id: $("#data_table").val(),
            biz_id: cc_biz_id,
        },
        success: function(result){
            if (result.result){
                var monitor_data = [{"id": "*", "text": "COUNT(*)", "type": "int", "desc": "COUNT(*)"}];
                var dimension_data = [];
                var ccset_data = [{"id": "*", "text": "全区全服"}]
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
                    // 大区字段
                    ccset_data.push({id: value["name"], text: text})
                });
            } else {
                dimension_data = [{"id": "", "text": "获取数据失败:"+result.message}];
            }
            
            $.each(field_list, function(){
            	if(this.type == "value"){
            		var select_data = monitor_data
            	}
            	else if(this.type == "dimension"){
            		var select_data = dimension_data
            	}
            	else{
            		var select_data = ccset_data
            	}
            	$("#"+this.id).select2({data:select_data, multiple:this.is_multiple, dropdownAutoWidth:"true"});
                if(this.type == "value" && scenario != "online"){
                    $("#"+this.id).select2("val", "*").trigger('change');
                } else {
            	   $("#"+this.id).select2("val", null).trigger('change');
                }
            })
            if(scenario != "custom" && $("input[name=biz_type]:checked").val() == "mobile"){
                $("#num_rules").trigger("change")
            }
        }
    })
}

/*
 * 保存监控配置
 */
 function save_monitor_config(operate_type, desc){
	 //验证参数
	 res = chek_base_config_parm();
	 console.log('chek_base_config_parm'+res);
	 if(!res){
	 	$("#save_config").attr("disabled", false);
         console.debug("res not")
	 	return ;
	 }	
    param = get_monitor_param();
    if (!('biz_id' in param)){
        param.biz_id = cc_biz_id
    }
    console.debug(param)
    if (!param){
        $("#save_config").attr("disabled", false);
        return
    }
    $("#save_config").html('<img alt="loadding" src="'+static_url+'img/loading_2_16x16.gif">提交中...');
    $.post(site_url+operate_type+"/", {param: JSON.stringify(param), biz_id: cc_biz_id}, function (feedback) {
        console.log(feedback);
        var type = '';
        if (feedback.result){
        	// monitor_id, 回调方法中需要
        	if(operate_type == 'access_custom' || operate_type == 'access_performance' ){
        		var type = feedback.data.type;
        		var monitor_id  = feedback.data.id;
        	}else{
        		var monitor_id  = feedback.data;
        	}
        	// 监控配置已经存在，则跳转到原有页面 
    		if(type == 'update'){
        		var msg = "该监控配置已经添加，不能重复添加";
        		var url = site_url + cc_biz_id + '/config/custom/'+monitor_id + '/';
    		    dialog({
    		        width: 430,
    		        title: '提示',
    		        ok: function() {
    		        	// 挑战到已有的配置页面
    		        	//window.location.href = url;
    		        	$("#iframe_body").load(url);
    		        },
    		        okValue: '跳转到已有监控配置',
    		        cancelValue: '取消',
    		        cancel: function (){},
    		        content: '<div class="king-notice-box king-notice-warning"><p class="king-notice-text">'+msg+'</p></div>'
    		    }).show();
    		}else{
    			alert_topbar(desc + "成功", "success");
    			//app_show(desc + "配置成功", 'success');
    			// 关闭并返回
    			setTimeout(function() {
    				var d = dialog({id: 'alert_tip'});
    				d.close().remove();
    				console.log('monitor_id:'+monitor_id);
    				close_div(iframeCallBack(monitor_id))
    			}, 1000);
    		}
    		$("#save_config").html('提交');
            //$("#save_config").attr("disabled", false);
        } else {
            app_alert(desc + "配置失败，请联系管理员："+feedback.message, "fail");
            $("#save_config").html('提交');
            $("#save_config").attr("disabled", false);
        }
    }, "JSON")
}
function app_show(msg, type) {
    dialog({
    	id: 'alert_tip',
        width: 260,
        title: '温馨提示',
        content: '<div class="king-notice-box king-notice-'+type+'"><p class="king-notice-text">'+msg+'</p></div>'
    }).show();
}
function app_alert(msg, type) {
    var d = dialog({
        width: 260,
        title: '温馨提示',
        cancel: function (){},
        ok: function() {},
        okValue: '确定',
        cancel: false,
        content: '<div class="king-notice-box king-notice-'+type+'"><p class="king-notice-text">'+msg+'</p></div>'
    })
    d.show();
    return d;
}
