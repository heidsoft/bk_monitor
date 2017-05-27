var FUNC_CHECK = (function(){
	return {
		switch_func: function(obj, status){
			/*开启、关闭功能开关*/
			var url = site_url+'switch_func/';
			$.post(url,{
				'status': status
			}, function(data){
				if(data.res){
					$('button[name="func_switch"]').removeClass('btn-success');
					$(obj).addClass('btn-success')
				}else{
					art.dialog({
						width: 460,
						height:200,
						fixed: true,
						lock: true, 
						content: data.msg
					});
				}
			}, 'json');
		},
		/*运行功能*/
		excute_func: function(obj){
			var url = site_url+'excute_func/';
			$.post(url,{
			}, function(data){
				art.dialog({
					width: 460,
					height:200,
					fixed: true,
					lock: true, 
					content: data.msg
				});
			},'json');
		}
	}

})();