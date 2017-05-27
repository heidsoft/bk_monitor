//格式化返回的list dict
function format_listdict(data, x, y, dict) {
    var data_list = []
    for (var i in  data) {
        var obj = data[i]
        var _x = obj[x]
        var _y = obj[y]
        if (dict[_x]) {
            data_list.push([dict[_x], _y])
        } else {
            data_list.push(["" + _x, _y])
        }
    }
    return data_list
}

//获得当前的时间,string格式
function get_current_time() {
    var fix_num = function(num){
        if (num >= 1 && num <= 9) {
            num = "0" + num;
        }
        return num
    }

    var date = new Date();
    var seperator1 = "-";
    var seperator2 = ":";
    var  month = fix_num(date.getMonth() + 1)
    var strDate = fix_num(date.getDate())
    var hour = fix_num(date.getHours())
    var minutes = fix_num(date.getMinutes())
    var second = fix_num(date.getSeconds())

    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
            + " " + hour + seperator2 + minutes
            + seperator2 + second;
    return currentdate;
}

// frequent method
function clone_obj(obj) {
    return jQuery.extend(true, {}, obj);
}
function datetime_to_unix(datetime) {
    var tmp_datetime = datetime.replace(/:/g, '-');
    tmp_datetime = tmp_datetime.replace(/ /g, '-');
    var arr = tmp_datetime.split("-");
    var now = new Date(Date.UTC(arr[0], arr[1] - 1, arr[2], arr[3] - 8, arr[4], 0));
    return parseInt(now.getTime());
}
function unix_to_datetime(unix) {
    var now = new Date(parseInt(unix));
    return now.toLocaleString().replace(/\//g, "-")
}

function unix_to_date(unix) {
    var now = new Date(parseInt(unix));
    var s = now.toLocaleString().replace(/\//g, "-")
    s = now.toLocaleString().replace(/\//g, "-")
    return s.split(" ")[0]
}


function removeHTMLTag(str) {
    str = str.replace(/<\/?[^>]*>/g, ''); //去除HTML tag
    str = str.replace(/<br>/g, ''); //去除HTML tag
    str = str.replace(/[ | ]*\n/g, '\n'); //去除行尾空白
    //str = str.replace(/\n[\s| | ]*\r/g,'\n'); //去除多余空行
    //str = str.replace(/ /ig, '');//去掉
    str = str.replace(/&nbsp;&nbsp;&nbsp;&nbsp;/g, '<br/>'); //去除行尾空白
    str = str.replace(/【/g, '<br/><br/>【')
    return str;
}
/*
 * 获得时间差,时间格式为 年-月-日 小时:分钟:秒 或者 年/月/日 小时：分钟：秒
 * 其中，年月日为全格式，例如 ： 2010-10-12 01:00:00
 * 返回精度为：秒，分，小时，天
 */
function GetDateDiff(startTime, endTime, diffType) {
//将xxxx-xx-xx的时间格式，转换为 xxxx/xx/xx的格式
    startTime = startTime.replace(/\-/g, "/");
    endTime = endTime.replace(/\-/g, "/");
//将计算间隔类性字符转换为小写
    diffType = diffType.toLowerCase();
    var sTime = new Date(startTime); //开始时间
    var eTime = new Date(endTime); //结束时间
//作为除数的数字
    var divNum = 1;
    switch (diffType) {
        case "second":
            divNum = 1000;
            break;
        case "minute":
            divNum = 1000 * 60;
            break;
        case "hour":
            divNum = 1000 * 3600;
            break;
        case "day":
            divNum = 1000 * 3600 * 24;
            break;
        default:
            break;
    }
    return parseInt((eTime.getTime() - sTime.getTime()) / parseInt(divNum));
}
