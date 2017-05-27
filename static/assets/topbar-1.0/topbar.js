/*!
 * topBar v1.0 
 * Copyright © 2012-2016 Tencent. All Rights Reserved.
 *  authors : shunbqiu 
 */

$(function() {
    var topBarTimline = 0;
    $topBar = function(options) {
        $div = $("<div class='magic-topbar-container'></div>");
        if ((typeof options == 'object') && options.constructor == Object) {
            // 设置默认值
            var defaults = {
                    setClass: 'bg-primary',
                    close: function() {},
                    timeOut: 0,
                }
                // 传参设置
            var options = $.extend(defaults, options);

            // 判断页面是否有提示条
            if ($('.magic-topbar-container').length>0) {
                $('.magic-topbar-container').remove();
                clearTimeout(topBarTimline);
            };
            if ($('.' + options.setClass).length == 0 ) {
                // 生成提示条
                $div.addClass(options.setClass).appendTo('body').html('<span>' + options.text + '</span>');
                // 添加关闭按钮
                $div.append('<div class="magic-topbar-close" style="font-size:20px; float:right;margin:-5px -15px 0 0;cursor:pointer;">&times;</div>');
                // 阻止冒泡和默认行为
                $div.on('click', function() {
                        return false;
                    })
                // 关闭按钮事件
                $('.magic-topbar-close').on('click', function() {
                        $(this).parent().remove();
                        options.close();
                        return false;
                    })
                // 设置默认关闭时间
                function closeFn() {
                    $('.magic-topbar-close').trigger('click');
                    clearTimeout(topBarTimline);
                }
                if (!options.timeOut == 0 && options.timeOut > 0) {
                    topBarTimline = setTimeout(closeFn, options.timeOut);
                };
                // 鼠标移入移出
                $div.mouseenter(function() {
                    clearTimeout(topBarTimline);
                });
                $div.mouseleave(function() {
                    if (!options.timeOut == 0 && options.timeOut > 0) {
                        topBarTimline = setTimeout(closeFn, options.timeOut);
                    };
                })
            };
        };

    }

})
