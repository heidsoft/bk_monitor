/**
 * Created by willgchen on 2016/5/18.
 */
Array.range= function(a, b, step){
    var A= [];
    if(typeof a== 'number'){
        A[0]= a;
        step= step || 1;
        while(a+step<= b){
            A[A.length]= a+= step;
        }
    }
    else{
        var s= 'abcdefghijklmnopqrstuvwxyz';
        if(a=== a.toUpperCase()){
            b=b.toUpperCase();
            s= s.toUpperCase();
        }
        s= s.substring(s.indexOf(a), s.indexOf(b)+ 1);
        A= s.split('');
    }
    return A;
};
function obj_to_query_string(obj) {
  var str = [];
  for(var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return '?' + str.join("&");
}
function query_string_to_obj(query_string){
    return (query_string || document.location.search).replace(/(^\?)/,'').split("&").map(function(n){return n = n.split("="),this[n[0]] = n[1],this}.bind({}))[0];
}

function app_confirm(msg, callback) {
    var d = dialog({
        width: 260,
        title: '操作确认',
        content: msg,
        okValue: '确定',
        ok: function() {callback()},
        cancelValue: '取消',
        cancel: function() {}
    });
    d.showModal();
   return d;
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
function app_tip(msg, type) {
    var d = dialog({
        width: 260,
        title: '温馨提示',
        content: '<div class="king-notice-box king-notice-'+type+'"><p class="king-notice-text">'+msg+'</p></div>'
    })
    d.show();
    return d;
}
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function all(iterable) {
    for (var index = 0; index < iterable.length; ++index) {
        if (!iterable[index]) return false;
    }
    return true;
}

function any(iterable) {
    for (var index = 0; index < iterable.length; ++index) {
        if (iterable[index]) return true;
    }
    return false;
}

// 求交集代码
function isDate(value) {
    return Object.prototype.toString.call(value) === '[object Date]';
}

function isRegExp(value) {
    return Object.prototype.toString.call(value) === '[object RegExp]';
}

function isFunction(value) {
    return typeof value === 'function';
}

function equals(o1, o2) {
    if (o1 === o2) return true;
    if (o1 === null || o2 === null) return false;
    var t1 = typeof o1, t2 = typeof o2, length, key, keySet;
    if (t1 == t2) {
        if (t1 == 'object') {
            if (Array.isArray(o1)) {
                if (!Array.isArray(o2)) return false;
                if ((length = o1.length) == o2.length) {
                    for (key = 0; key < length; key++) {
                        if (!equals(o1[key], o2[key])) return false;
                    }
                    return true;
                }
            } else if (isDate(o1)) {
                if (!isDate(o2)) return false;
                return equals(o1.getTime(), o2.getTime());
            } else if (isRegExp(o1) && isRegExp(o2)) {
                return o1.toString() == o2.toString();
            } else {
                //if (isScope(o1) || isScope(o2) || isWindow(o1) || isWindow(o2) || Array.isArray(o2)) return false;
                keySet = {};
                for (key in o1) {
                    if (key.charAt(0) === '$' || isFunction(o1[key])) continue;
                    if (!equals(o1[key], o2[key])) return false;
                    keySet[key] = true;
                }
                for (key in o2) {
                    if (!keySet.hasOwnProperty(key) &&
                        key.charAt(0) !== '$' &&
                        o2[key] !== undefined && !isFunction(o2[key])) return false;
                }
                return true;
            }
        }
    }
    return false;
}

function intersection(array) {
    var result = [];
    var argsLength = arguments.length;
    for (var i = 0; i < array.length; i++) {
        var item = array[i];
        if (contains(result, item)) continue;
        for (var j = 1; j < argsLength; j++) {
            if (!contains(arguments[j], item)) break;
        }
        if (j === argsLength) result.push(item);
    }
    return result;
}

function contains(obj, target) {
    if (obj == null) return false;

    var flag = false;
    for (var i = 0; i < obj.length; i++) {
        if (equals(obj[i], target)) {
            flag = true;
        }
    }

    return flag;
}