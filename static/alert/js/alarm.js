$(document).ready(function(){

    var solution_type = {
        "success": "success",
        "~success": "failure",
    }

  

    // var solution_data= [
    //     [{1: ["success"], 2: ["~success"]}, 1729, "[1729] 10min汇总", "success"],
    //     [{}, 1729, "[1729] 10min汇总", "noway"],
    //     [{}, 1729, "[1729] 10min汇总", "failure"],
    // ]

    // var data = {
    //     "nodes": [
    //         { "id": "window1", "text": "node1", height : '60', width : '130', className:"success"},
    //         { "id": "window2", "text": "node2", height : '60', width : '130', className:"success"},
    //         { "id": "window3", "text": "node3", height : '60', width : '130', className:"success"},
    //         { "id": "window4", "text": "node4", height : '60', width : '130', className:"failure"}
    //     ],
    //     "edges": [
    //          { "source": "window1", "target": "window2", edgesType:"success"},
    //          { "source": "window1", "target": "window3", edgesType:"failure"},
    //          { "source": "window2", "target": "window4", edgesType:"failure"}
    //     ]
    // };

    var data = transform_solution_data(solution_data, solution_type)

    bk = $('#bktopo').bkTopology({
        data:data,  //配置数据源
        autoPosition:true,
        readonly:true,  //是否可编辑
        lineType:[  //配置线条的类型
            {type:'success',value:'成功',lineColor:'#46c37b'},
            {type:'failure',value:'失败',lineColor:'red'},
            {type:'skip',value:'跳过',lineColor:'#888580'},
            {type:'authorize',value:'授权',lineColor:'#3675c5'},
            {type:'check',value:'检查',lineColor:'#f3b760'}
        ],
        onDbLineClick:function(event,data){  //点击连线的时候触发
            var thisSource = $(this).data().source;
            var count = 0;            
            data.forEach(function(v,i){
                if(v.source == thisSource){
                    count++;
                }
            });
            if(count>1){
                alert('删除路径');
               bk.remove($(this));
            }
        },
        onConnection:function(event,ldata){
            //return false;
            // 连线的时候触发该事件，return false 可阻止联线;
            edge_list = bk.getEdges();
            for (var i in edge_list){
                if(edge_list[i].source == ldata.source && edge_list[i].target == ldata.target){
                    bk.remove($('[data-id="'+edge_list[i].id+'"]'))
                    break
                }
            }
            // $("#real_solutions").val($.toJSON(transform_data(data)));
        }
    });
    
    bk.reLoad()
    // $('#bktopo').on('click','.fa-refresh', function(e){
    //     alert("shit")
    // })
})


function transform_solution_data(solution_data, solution_type){
    var nodes = []
    var edges = []
    //加入node_id
    for(var i in solution_data){
        var id = get_uuid();
        solution_data[i].push(id)
    }
    for(var i in solution_data){
        nodes.push({"id": solution_data[i][4], "text": solution_data[i][2], "solution_id": solution_data[i][1], className: solution_data[i][3], height: '60', width: '130'})
        var relation = solution_data[i][0]
        if(relation != {}){
            for(var re in relation){
                edges.push({"source": solution_data[i][4], "target": solution_data[re][4], edgesType: solution_type[relation[re][0]]})
            }
        }
    }
    return {"nodes": nodes, "edges": edges}
}

function get_uuid(){
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
}

