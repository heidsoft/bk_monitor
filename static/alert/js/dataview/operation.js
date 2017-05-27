/**
 * Created by willgchen on 2016/5/9.
 */

var eventColor = {
    // 级别
    info: '#888686',
    warning: '#4a9bff',
    critical: '#d26a5c',
    // 是否处理
    error: '#CC0000',
    ok: '#006600'
};

var event_color = function(event_level){
    var color = eventColor.critical;
    switch(event_level){
        case "3":
        case 3:
            color = eventColor.info;
            break;
        case "2":
        case 2:
            color = eventColor.warning;
            break;
        case "1":
        case 1:
            color = eventColor.critical;
            break;
    }
    return color
};
