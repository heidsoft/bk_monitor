(function($){
	function Topology(config){
		this.config = config;
		this.curDom = config.curDom;
		this.data = config.data;
		this.lineBtnGroup ={};
		this.lineColor =[];
		this.initEvent(this.curDom);
		this.dragToConnection();
		this.topologyContainerInfo =[];
		this.topologyContainerInfo['w'] = 0;
		this.topologyContainerInfo['h'] = 0;
	}
	Topology.prototype = {
		constructor : Topology,
		init:function(){	// 初始化
			this.curDom.addClass('topology-container');
			this.initLineBtn(this.config.lineType);
			if(this.config && this.config.autoPosition){
				this.autoPosition(this.data);
			}
			this.initData(this.data,this.curDom);

			var curDomWidth = Number(this.curDom.css('width').replace('px',''));
			var curDomHeight = Number(this.curDom.css('height').replace('px',''));
			if(!curDomWidth){
				curDomWidth = this.curDom[0].clientWidth
			}
			if(!curDomHeight){
				curDomHeight = this.curDom[0].clientHeight
			}

			if(curDomWidth <this.topologyContainerInfo['w'] || curDomHeight <this.topologyContainerInfo['h']){
				this.reSize();
			}
			this.readWriteMode();			
		},	
		reSize:function(){	//重新设置大小
			this.curDom.css({
				width:(this.topologyContainerInfo['w']+200)+'px',
				height:(this.topologyContainerInfo['h']+200)+'px'
			});
		},
		readWriteMode:function(){	//编辑和预览模式的差异处理
			if(this.config.readonly){
				this.curDom.find('.option-group').addClass('none');
				this.curDom.find('.option-group').addClass('none');
				this.curDom.find('.node-text').css('padding-bottom','5px');
				this.curDom.find('[data-type="close"]').addClass('none');
			}else{
				this.curDom.find('[data-type="refresh"]').addClass('none');
			}			
		},
		autoPosition:function(data){	//dagre 库计算线条位置
			var topThis = this;
			var g = new dagre.graphlib.Graph();
			g.setGraph({});      		
			g.setDefaultEdgeLabel(function() { return {};});

      		data.nodes.forEach(function(v,i){g.setNode(v.id, v); });
      		data.edges.forEach(function(v,i){g.setEdge(v.source, v.target,{}); });
      		dagre.layout(g);
      		 
			var temp = [];
      		g.edges().forEach(function(e){
      			topThis.data.edges.forEach(function(v){
      				if(e.v == v.source && e.w == v.target){
      					temp.push({
		      				"source":e.v,
		      				"target":e.w,
		      				"points":g.edge(e).points,
		      				"edgesType":v.edgesType
		      			})		
      				}	
      			})
			});
			topThis.data['edges'] = temp; 
		},
		drawNode:function(v){	//根据数据绘制节点
			var uid="";
			if(v && v.id && v.id.length>1){
				uid = v.id;
			}else{
				uid = this.getUUid();
			} 
			if(this.topologyContainerInfo['w'] < Number(v.x)){this.topologyContainerInfo['w'] = Number(v.x); }
			if(this.topologyContainerInfo['h'] < Number(v.y)){this.topologyContainerInfo['h'] = Number(v.y); }

			var templates = $('#node-templates').clone().removeAttr('id')
				.removeClass("none").attr('data-id',uid)
				.css({
					top:(v.y-v.height/2)+'px',
					left:(v.x-v.width/2)+'px',					
					width:v.width
				});

			if(v.className){
				templates.addClass(v.className);
			}
			templates.find('.node-text').html(v.text);
			templates.find('i').attr('data-node-id',uid);
			templates.data('dataType',"node");			

			delete v.id;
			delete v.text;
			delete v.height;
			delete v.width;
			delete v.x;
			delete v.y;
			delete v.source;
			delete v.target;

			this.curDom.append(templates);

			Object.keys(v).forEach(function(v1,i1){	//将额外的信息保存到节点的缓存中
				var temp = {};
				temp[v1] = v[v1];
				templates.data(temp);
			});						
		},
		initData:function(data){	//初始化节点和线条
			var topThis = this;			
			data.nodes.forEach(function(v,i){
				topThis.drawNode(v);
			});
			data.edges.forEach(function(v,i){
				topThis.drawPathNew(v);
			});
		},
		createSvgContainer:function(source,target){
			var sourceInfo =[] ,targetInfo=[],svgdivInfo=[];
			/*获取源节点信息*/
			sourceInfo['l'] = source.position().left;
			sourceInfo['t'] = source.position().top;
			sourceInfo['w'] = source.innerWidth();
			sourceInfo['h'] = source.innerHeight();
			/*目标源节点信息*/
			targetInfo['l'] = target.position().left;
			targetInfo['t'] = target.position().top;
			targetInfo['w'] = target.innerWidth();
			targetInfo['h'] = target.innerHeight();

			svgdivInfo['w'] = (sourceInfo['l']+sourceInfo['w']/2)-(targetInfo['l']+targetInfo['w']/2);
			svgdivInfo['w'] = svgdivInfo['w'] < 0 ? svgdivInfo['w']*-1 :svgdivInfo['w'];

			/*生成div信息*/
			if(sourceInfo['l']>targetInfo['l']){
				svgdivInfo['l'] = targetInfo['l'] + targetInfo['w']/2;
			}else if(sourceInfo['l']<targetInfo['l']){
				svgdivInfo['l'] = sourceInfo['l'] + sourceInfo['w']/2;
			}else{
				svgdivInfo['l'] = sourceInfo['l'] + sourceInfo['w']/2;
			}

			if(targetInfo['t'] > sourceInfo['t']){
				svgdivInfo['h'] = (targetInfo['t']) - (sourceInfo['t'] + sourceInfo['h']);	
				svgdivInfo['t'] = (sourceInfo['t'] + sourceInfo['h']);
			}else if(targetInfo['t'] < sourceInfo['t']){
				svgdivInfo['h'] = (sourceInfo['t']) - (targetInfo['t'] + targetInfo['h']);	
				svgdivInfo['t'] = (targetInfo['t'] + targetInfo['h']);
			}

			var data={				 
				targetInfo:targetInfo,
				sourceInfo:sourceInfo,
				svgdivInfo:svgdivInfo				
			}		    
		    return data; 
		},
		drawPathNew:function(data){

			var d = "";
			var temp ="";
			data.points.forEach(function(v,i){
				temp+= " "+v.x+" "+v.y;				 
				if(data.points[i-1]){
					var m = data.points[i-1];
				 	d += " M "+m.x+" "+m.y+" L "+v.x+" "+v.y;
				}else{
				 	d += " M "+v.x+" "+v.y;
				}
			})

			var arrowPos = data.points[data.points.length-1];
			var arrow =[];
			var ax = arrowPos.x,ay= arrowPos.y;
				arrow['d'] = 'M '+ax+' '+ay +' L'+(ax-5)+' '+(ay-10)+' L '+ax+' '+(ay-7)+' L '+(ax+5)+' '+(ay-10)+' L'+ ax+' '+ay;

			var data_uid = this.getUUid();			

			var tempPath =$('<svg style="width: 100%;height: 100%;" pointer-events="none">'+
		            		'<path data-id="'+data_uid+'" d="'+d+'" pointer-events="visibleStroke" stroke="'+this.lineColor[data.edgesType]+'" stroke-width="2px";"></path>'+
		            		'<path d="'+arrow['d']+'" stroke="'+this.lineColor[data.edgesType]+'" fill="'+this.lineColor[data.edgesType]+'" class="node-path" style="stroke-width: 1px;"></path>'+
		         	  	'</svg>');
		   
		   	var result = this.curDom.append(tempPath);

		   	var target =$('[data-id="'+data.target+'"]');
		   	var source =$('[data-id="'+data.source+'"]');		   	

		    /*设置jQuery data()*/
			var jDataS =target.data('source');
			var jDataT =source.data('target');

			tempPath.find('path[data-id]').data({source:source.attr('data-id'),target:target.attr('data-id'),dataType:'path',edgesType:data.edgesType});
		    source.data({'target':jDataT == undefined ? target.attr('data-id'):jDataT+','+target.attr('data-id')});
		    target.data({'source':jDataS == undefined ? source.attr('data-id'):jDataS+','+source.attr('data-id')});
		    
		    return result;
 
		},	
		getUUid:function(){
			var s = [];
		    var hexDigits = "0123456789abcdef";
		    for (var i = 0; i < 36; i++) {
		        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
		    }
		    s[14] = "4";  
		    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1); 
		    s[8] = s[13] = s[18] = s[23] = "-";
		    		 
		    var uuid = s.join("");
		    return uuid;
		},
		initLineBtn:function(lineType){
			var temp = '<div class="lines-option">';
			var tempArray = [];
			lineType.forEach(function(v,i){
				temp += '<span data-type="'+v.type+'">'+v.value+'</span>';
				tempArray[v.type] = v.lineColor;				
			})
			this.lineColor = tempArray;
			temp += "</div>";
			this.lineBtnGroup = $(temp);
		},
		getNodes:function(){
			var tempArray = [];
			this.curDom.find('.node').each(function(i,v){
				var dom = $(v),temp = $(v).data();
				temp.id = dom.attr('data-id');
				temp.text = dom.find('.node-text').html();
				temp.height = dom.css('height').replace('px','');
				temp.width = dom.css('width').replace('px','');				
				tempArray.push(temp);
			});
			return tempArray;
		},
		getEdges:function(){
			var tempArray = [];
			this.curDom.find('path[data-id]').each(function(i,v){
				var dom = $(v);
				var jqData = dom.data();				 
				tempArray.push(jqData);
			})
			return tempArray;
		},
		remove:function(arguments){			
			var jqDom,topThis = this;
			if(arguments[0] && typeof(arguments[0]) == 'string'){
				jqDom = $(arguments[0]);
			}else if(arguments[0] instanceof jQuery){
				jqDom = arguments[0];
			}else{
				return ;
			}
			var dataId = jqDom.attr('data-id');

			if(dataId){
				var jqData = jqDom.data();
					
				if(jqData.dataType == 'node'){
					topThis.getEdges().forEach(function(v,i){
						if(v.source == dataId || v.target == dataId){
							topThis.curDom.find('[data-id="'+v.id+'"]').parent().remove();
						}				
					})
					jqDom.remove();
				}else if(jqData.dataType == 'path'){
					jqDom.parent().remove();
				}
			}
		},
		reLoad:function(){			
			this.data['nodes'] = this.getNodes();
			this.data['edges'] = this.getEdges();

			if(arguments[0] && arguments[0]['nodes']){
				this.data['nodes'].push(arguments[0]['nodes']);				
			}

			if(arguments[0] && arguments[0]['edges']){
				this.data['edges'].push(arguments[0]['edges']);
			}
			
			this.curDom.empty();
			this.init();
		},
		dragToConnection:function(){
			var isMouseDown =false;
			var topThis = this;
			var position = [];
			var edgesType ="";
			var dataId=null;
			var nodeChildrenClassArray =[];

			this.curDom.on('mousedown','.node',function(e){
				var className = $(e.toElement).prop('class');
				dataId = $(this).attr('data-id');
				if(className && className.indexOf('option-btn') != -1){					
					getChildrenClassName();
					isMouseDown = true;
					position['start_x'] = e.pageX;
					position['start_Y'] = e.pageY;					
			        if(className.indexOf('success') != -1){
			            edgesType= 'success';
			        }else if(className.indexOf('failure') != -1){
			            edgesType= 'failure'
			        }else if(className.indexOf('other') != -1){
			            edgesType= 'check'
			        }
			        var tempPath =$('<svg style="width: 100%;height: 100%;" pointer-events="none">'+
		            		'<path class="dragToConnectionSvge" d="" pointer-events="visibleStroke" stroke-width="2px";"></path>'+
		            		/*'<path d="'+arrow['d']+'" stroke="'+this.lineColor[data.edgesType]+'" fill="'+this.lineColor[data.edgesType]+'" class="node-path" style="stroke-width: 1px;"></path>'+*/
		         	  	'</svg>');
					topThis.curDom.append(tempPath); 

			        topThis.curDom.find('.dragToConnectionSvge').attr({
			        	"stroke":topThis.lineColor[edgesType],
			        	"fill":topThis.lineColor[edgesType]
			        })
				}				
			})
			.on('mouseup',function(e){
				var className = $(e.toElement).prop('class');				
				try
				{
				   	className = className.split(' ');
				   	if(className.length>0 && nodeChildrenClassArray.indexOf(className[className.length-1]) != -1){
				   		var nodeId = $(e.toElement).parentsUntil('.topology-container').find('i').data('nodeId');
				   		if(nodeId && nodeId != dataId){				   				
				   			var result = topThis.config.onConnection.apply(this,[e,{"source": dataId,"target": nodeId,"edges":topThis.getEdges()}]);
				   			if(result == false){					
								return;
							}	
				   			var temp = [];
					        temp['edges'] ={"source": dataId, "target": nodeId, edgesType:edgesType}
				   			topThis.reLoad(temp)			   			
				   		}
					}
				}catch(err){
				   
				}finally{
					topThis.curDom.find('.dragToConnectionSvge').parent().remove();
					isMouseDown = false;
				}				
			})
			.on('mousemove',function(e){
				if(isMouseDown){
					showLine(e);
				}
			}) 
			function showLine(e){
				var y = Number(topThis.curDom.css('top').replace('px',"").replace('auto','0'));
				var x = Number(topThis.curDom.css('left').replace('px',"").replace('auto','0'));

				var d = " M "+(position['start_x'] - x) +" "+(position['start_Y']-y )+ " L "+(e.pageX -x)+" "+(e.pageY-y);
				topThis.curDom.find('.dragToConnectionSvge').attr('d',d);
			}			
			function getChildrenClassName(){
				if(nodeChildrenClassArray.length == 0){
					var temp ="";					
					topThis.curDom.find('.node:eq(0) *').each(function(i,v){
						temp += $(v).prop('class')+" ";
					});					
					nodeChildrenClassArray = temp.split(' ');
					nodeChildrenClassArray[nodeChildrenClassArray.length-1] ='node';
				}
			}
		},
		initEvent:function(curDom){
			var topThis = this;
			var isMouseDown = false;
			var mouseXY = [];
			 
			curDom
			/*.on('mouseleave','.lines-option',function(e){
				e.stopPropagation();
				e.preventDefault();
				$('.lines-option').remove();
			})
			.on('click','.lines-option span',function(e){
				e.stopPropagation();
				e.preventDefault();
				var result = topThis.config.onConnection.apply(this,[e,topThis.getEdges()]);
				if(result == false){					
					return;
				}
				var $this = $(this);
				var type = $this.attr('data-type');
				var source = $('.node-selected:eq(0)');
				var target = $(this).parent().prev();
				var result = topThis.drawPath(source,target,type);
				if(result){
					$('.node-selected').removeClass('node-selected');
					$('.lines-option').remove();
				}
			})*/
			.on('mouseenter','svg path',function(e){
				e.stopPropagation();
				e.preventDefault();
				$(this).css({
					'stroke-width':'5px',
					'z-index':'1'
				});
			})
			.on('mouseleave','svg path',function(e){
				e.stopPropagation();
				e.preventDefault();
				$(this).css({
					'stroke-width':'2px',
					'z-index':'inherit'
				});
			})
			.on('dblclick',"svg path",function(e){
				e.stopPropagation();
				e.preventDefault();
				topThis.config.onDbLineClick.apply(this,[e,topThis.getEdges()]);	//配置参数中的事件处理
			})
			.on('mousemove',function(e){				
				if(isMouseDown){					
					var move = [],moveTo = [],div = [];
					var $this = $(this);
					 
					move['x'] = e.pageX;
					move['y'] = e.pageY;

					moveTo['t'] = move['y'] - mouseXY['y'];
					moveTo['l'] = move['x'] - mouseXY['x'];
					
					curDom.css({
						'top':moveTo['t']+mouseXY['top'],
						'left':moveTo['l']+mouseXY['left']
					})
				}				
			}).on('mousedown',function(e){
				mouseXY['x'] = e.pageX;
				mouseXY['y'] = e.pageY;
				mouseXY['top'] = Number(curDom.css('top').replace('px',"").replace('auto',"0"));
				mouseXY['left'] = Number(curDom.css('left').replace('px',"").replace('auto',"0"));
				if($(this).prop('class') == $(e.toElement).prop('class')){
					isMouseDown = true;	
				}				
			}).on('mouseup',function(e){
				isMouseDown = false;
				mouseXY=[];
			})

			$('body').on('mouseup',function(e){
				isMouseDown = false;
				mouseXY=[];
			})
		}
	}

	$.fn.bkTopology = function(config){
		config.curDom = $(this)
		var topo={}; 
		if(typeof(arguments[0]) == 'object'){
			if($(this).prop('class').indexOf('topology-container') ==-1){
				topo = new Topology(config);
				topo.init();
			}
		}
		var methods={
			remove:function(){
				topo.remove(arguments);
			},
			getConfig:function(){
				return config;
			},
			getNodes:function(){
				return topo.getNodes();
			},
			getEdges:function(){
				return topo.getEdges();
			},
			reLoad:function(arguments){
				topo.reLoad(arguments);
			},
			getUUid:function(){
				return topo.getUUid();
			}
		}
		return methods;
	}
})(jQuery);

