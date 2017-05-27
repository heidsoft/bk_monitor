/**
 * @module: 输入框形态
 * @author: robyi
 * @contributors: cache <cache@tencent.com>
 * @create: 2013-11-26
 * @update: 2015-09-29
 * @version: 1.1.0
 * @requires: jQuery
 */
;(function ($) {

	'use strict';

	$.fn.extend({

		/**
		 * memberInput
		 * @param {Object} options 配置对象
		 */
		memberInput: function (options) {

			/**
			 * 默认配置项
			 */
			var defaultOptions = {
				// 数据源
				allMemberUrl: 'http://lib.cdc.com/oaui/memberinput/data/allmember.php',
				// 是否允许输入邮件组
				allowMailGroup: false,
				// 自定义组件类
				className: '',
				// 是否自动聚焦到组件
				autoFocus: false,
				// 最大提示数量，最多显示 8 个
				maxTipsCount: 5,
				// 初始化回调
				onInit: $.noop,
				// 邮件组前缀
				groupPrefix: []
			}

			// 提取配置
			options = $.extend({}, defaultOptions, options)

			// 最大提示数量控制
			options.maxTipsCount = options.maxTipsCount > 8 ? 8 : options.maxTipsCount

			// 邮件组前缀正则全局提取
			var groupPrefix = ['g_', 'c_'].concat(options.groupPrefix)
			var groupMailPrefix = groupPrefix.join('|')
			var groupMailRegExp = new RegExp('^(' + groupMailPrefix + ')\\w+','i')

			// 所有候选人列表，从服务器动态提取
			var allMemberList

			/**
			 * MemberInput 构造器
			 * @param {Object} $input 原始输入框元素
			 */
			var MemberInput = function ($input) {

				this.$input = $input
				// 已输入的值
				this.memberPickerValue = []
				// 当前选中的tips
				this.tipsIndex = 0
				// 当前tips数量
				this.tipsCount = 0

				// 组件 UI 初始化
				this.uiInit()
				// 人员数据初始化
				this.dataInit()

				// this.showHistoryTips()
			}

			/**
			 * 组件 UI 初始化
			 */
			MemberInput.prototype.uiInit = function () {
				var _this = this
				// 组件容器
				this.$wrapper = $('<div class="oaui_memberinput_wrapper"></div>')
				this.$wrapper.addClass(options.className)
				// 编辑框
				this.$editor = $('<div class="oaui_memberinput_editor"></div>')
				// 插入编辑框
				this.$wrapper.append(this.$editor)

				if (options.$tips) {
					this.$tips = options.$tips
				} else {
					// 提示框
					this.$tips = $('<div class="oaui_memberinput_tips"><ul></ul></div>')
					// 插入提示框
					this.$wrapper.append(this.$tips)
				}

				// 默认隐藏提示框
				this.$tips.hide()
				// 在原始输入框后面插入组件
				this.$input.hide().after(_this.$wrapper)

				// 组件初始化回调
				if (options.onInit !== $.noop && typeof options.onInit === 'function') {
					options.onInit(this.$input)
				}

				// 绑定事件
				this.bindEvent()

			}

			/**
			 * 配置输入控件
			 * @param {Object} config 输入控件位置信息
			 */
			MemberInput.prototype.setFocus = function (config) {

				var $focusElem = $('<input type="text" />')
				var $target
				var method = 'append'

				if (config.direction) {
					var elementMethod = 'prev'
					method = 'before'
					if (config.direction === 'right') {
						elementMethod = 'next'
						method = 'after'
					}

					$target = this.$editor.find('input[type=text]')[elementMethod]()

					if (!$target.length) {
						return
					}
				} else {
					var x = config.x
					var y = config.y

					$target = this.$editor
					method = 'append'

					var $allMember = this.$editor.find('span.oaui_memberinput_member')

					// 用于标记当前比较的span的Y值
					var tempY
					// 用于标记当前插入的行位置
					var yIndex = -1
					// 用于标记当前行的坐标前一个元素
					var xTarget = []
					// 用于标记当前行的坐标前一个元素的前一个兄弟元素（光标在开头时xTarget为空）
					var xTargetPrev = []

					$allMember.each(function () {

						var $this = $(this)
						var thisPosition = $this.position()

						if (y > thisPosition.top) {
							if (tempY !== thisPosition.top) {
								yIndex++
								tempY = thisPosition.top
							}
							if (x > thisPosition.left + $this.width()) {
								xTarget[yIndex] = $this
							} else {
								if (!xTargetPrev[yIndex]) {
									xTargetPrev[yIndex] = $this.prev()
								}
							}
						}

					})

					$target = xTarget[yIndex]

					if (!$target) {
						// 点击每行开头
						$target = xTargetPrev[yIndex]
						method = 'after'
						if (!$target || !$target.length) {
							// 第一行第一个
							$target = $allMember.eq(0)
							method = 'before'
							if (!$target.length) {
								$target = this.$editor
								method = 'append'
							}
						}
					} else {
						// 点击每行非开头
						method = 'after'
					}
				}

				this.$editor.find('input[type=text]').remove()
				$target[method]($focusElem)

				setTimeout(function () {

					// 默认聚焦处理
					if (options.autoFocus) {
						$focusElem.focus()
					}

					// 兼容IE input事件
					$focusElem.on('propertychange',function () {
						$(this).trigger('input')
					})

				}, 0)

			}

			/**
			 * 输入完成处理
			 * @param  {Object}  dom               Editor 输入框
			 * @param  {Boolean} shouldContinue    是否继续处理
			 */
			MemberInput.prototype.inputFinished = function (dom, shouldContinue) {

				var _this = this

				var $input = $(dom)
				var value = $input.val()

				// 解析输入，邮件组处理
				var inputMemberArr = _this.parseString(value)
				inputMemberArr = _this.validateNames(inputMemberArr)

				_this.setHistory(inputMemberArr)

				var namePos =  $input.prevAll('.oaui_memberinput_member').length
				_this.concatMemberArr(namePos,inputMemberArr)

				_this.hideTips()

				// 更新输入框内容
				this.$input.val(this.getValue())

				var htmlStr = inputMemberArr.map(function (name) {
					// 分号用于选定后复制出去的场景…… :(
					return '<span class="oaui_memberinput_member">' + name +
							'<em class="oaui_memberinput_semicolon">;</em></span>'
				}).join('')

				var $member = $(htmlStr)

				try {
					if (shouldContinue) {
						$input.before($member).val('')
						_this.adjustInputSize(0)
					} else {
						if ($.trim(htmlStr)) {
							$input.replaceWith($member)
						}
					}
				} catch (e) {
					// @todo throw error
				}

			}

			/**
			 * 删除操作
			 * @param  {String} direction 删除方向，向前或者向后删除
			 */
			MemberInput.prototype.inputDelete = function (direction) {

				var $target = this.$editor.find('input')[direction]()
				var targetName = $target.text().replace(/;/g,'')

				if ($target && $target.length) {
					$target.remove()
				}

				this.removeFromMemberArr(targetName)

			}

			/**
			 * 动态调整输入框尺寸
			 * @param  {Number} size 输入字符数量
			 */
			MemberInput.prototype.adjustInputSize = function (size) {
				var _this = this
				setTimeout(function () {
					_this.$editor.find('input').width((size + 1) * 11)
				}, 0)

			}

			/**
			 * 显示提示
			 * @param  {String} value 生成提示的 memberString
			 */
			MemberInput.prototype.showTips = function (value) {

				if (!value || !allMemberList || !allMemberList.length) {
					return
				}

				var ret = []
				var highlightRegExp = new RegExp('^(' + value + ')','i')

				if (allMemberList.indexOf(value.toLowerCase()) > -1 && this.memberPickerValue.indexOf(value) < 0) {
					ret.push(value)
				}

				var i, len
				for (i = 0, len = allMemberList.length; i < len; i++) {

					if (allMemberList[i].toLowerCase().indexOf(value.toLowerCase()) === 0) {

						// 已经输入值不再出现
						if (this.memberPickerValue.indexOf(allMemberList[i]) < 0 && ret.indexOf(allMemberList[i]) < 0) {
							ret.push(allMemberList[i])
						}

						if (ret.length >= options.maxTipsCount) {
							break
						}
					}
				}

				this.tipsCount = ret.length

				// @todo map 兼容 
				var tipsHtml = ret.map(function (tipsItem) {

					return '<li><a href="javascript:;"><div class="avatar"><span style="background-image: url(http://dcloud.oa.com/Public/Avatar/' + tipsItem + '.png);"></span></div>' + tipsItem.replace(highlightRegExp,'<em class="oaui_memberinput_highlight">$1</em>') + '</a></li>'

				}).join('')

				this.$tips.show().find('ul').html(tipsHtml)

				this.rollTips(0)

			}

			// 隐藏提示
			MemberInput.prototype.hideTips = function () {

				this.$tips.hide()

			}

			/**
			 * 切换选择提示条目
			 * @param  {Number} index 条目索引
			 */
			MemberInput.prototype.rollTips = function (index) {
				var _this = this

				if (typeof index === 'string') {
					if (index === 'prev') {
						index = _this.tipsIndex - 1
					} else if (index === 'next') {
						index = _this.tipsIndex + 1
					}
				}

				if (typeof index === 'undefined') {
					index = 0
				}

				this.tipsIndex = index % this.tipsCount

				if (this.tipsIndex < 0) {
					_this.tipsIndex += _this.tipsCount
				}

				this.$tips.find('ul li').removeClass('oaui_memberinput_tips_active').eq(_this.tipsIndex).addClass('oaui_memberinput_tips_active')

			}

			/**
			 * 选择提示条目
			 * @param  {Number} index 条目索引
			 */
			MemberInput.prototype.selectTips = function (index) {

				if (this.$tips.is(':visible')) {

					if (typeof index === 'undefined') {
						index = this.tipsIndex
					}

					var value = this.$tips.find('ul li:eq(' + index + ')').text()

					var $input = this.$editor.find('input')
					$input.val(value)

					this.inputFinished($input.get(0), true)
				}

			}

			/**
			 * 数据初始化，从服务器上拉取所有的成员列表
			 */
			MemberInput.prototype.dataInit = function () {
				var _this = this

				if (!allMemberList || !allMemberList.length) {

					$.ajax({
						url:options.allMemberUrl,
						dataType:'jsonp'
					}).done(function (data) {

						if (data.status) {
							allMemberList = data.data.split(',')
						}

					}).fail(function () {
						// @todo fail 提醒
					})

				}

				if (_this.$input.val()) {

					var existValue = _this.$input.val()

					if (Array.isArray(existValue)) {
						existValue = existValue.join(';')
					}

					_this.setFocus({
						x: 0,
						y: 0
					})

					_this.$editor.find('input').val(existValue)
					_this.inputFinished(_this.$editor.find('input').get(), true)

				} else {
					_this.setFocus({
						x: 0,
						y: 0
					})
				}

			}

			/**
			 * 解析用户输入，处理各种输入法的问题
			 * @param  {String} string 用户输入
			 * @return {String} 提取合适的输入
			 */
			MemberInput.prototype.parseString = function (string) {

				string = string.replace(/[,;；、 ]/g, ';').replace(/\<.*?\>/g,'')
						.replace(/\(.*?\)/g,'')
						.replace(/@[\w\.-]*/g,'')

				var ret = string.split(';').filter(function (name) {
					return name
				})

				return ret

			}

			/**
			 * 验证输入
			 * @param  {Array} nameArr 验证源
			 * @return {Array}         过滤后的结果
			 */
			MemberInput.prototype.validateNames = function (nameArr) {
				
				var _this = this
				var ret = []

				// @todo forEach 兼容
				nameArr.forEach(function (name) {
					// 处理邮件组
					if (!allMemberList || !allMemberList.length || (options.allowMailGroup && groupMailRegExp.test(name))) {
						ret.push(name)
					} else {
						var targetIndex = -1
						var inAllMember = allMemberList.some(function (allMemberItem,index) {
							if (allMemberItem.toLowerCase() === name.toLowerCase()) {
								targetIndex = index
								return true
							} else {
								return false
							}
						})

						var inValue = _this.memberPickerValue.some(function (valueItem) {
							return valueItem.toLowerCase() === name.toLowerCase()
						})

						if (inAllMember && !inValue) {
							ret.push(allMemberList[targetIndex])
						}

					}

				})

				return ret

			}

			/**
			 * 成员插入操作
			 * @param  {Number} position 
			 * @param  {Array} nameArr 
			 */
			MemberInput.prototype.concatMemberArr = function (position,nameArr) {

				var nameArr1 = this.memberPickerValue.slice(0,position)
				var nameArr2 = this.memberPickerValue.slice(position)

				this.memberPickerValue =  nameArr1.concat(nameArr, nameArr2)

			}

			/**
			 * 移除成员
			 * @param  {String} nameStr 要移除的
			 * @return {Array}          移除后的
			 */
			MemberInput.prototype.removeFromMemberArr = function (nameStr) {

				this.memberPickerValue = this.memberPickerValue.filter(function (name) {
					return nameStr !== name
				})

			}

			/**
			 * 初始化时间绑定
			 */
			MemberInput.prototype.bindEvent = function () {

				// 点击出现输入框
				this.bindEditorClick()
				// 输入完成时处理数据
				this.bindInputFinished()
				// 退格或者删除
				this.bindDelete()
				// 输入时智能提示
				this.bindInputTips()
				// 动态调整输入框大小
				this.bindInputSize()
				// 粘贴
				this.bindPaste()
				// 原始输入框 change
				this.bindChange()

			}

			/**
			 * 点击 Editor 处理输入框
			 */
			MemberInput.prototype.bindEditorClick = function () {
				
				var _this = this

				// 先移除已经有的 input
				this.$editor.find('input[type=text]').remove()

				// 以下代码用于判断点击过程中是否有移动
				// 如果有移动，则可能是选定动作，不设焦点
				var shouldSetFocus = false

				var oldX
				var oldY

				this.$editor.on('mousedown',function (e) {

					shouldSetFocus = true
					oldX = e.pageX
					oldY = e.pageY

				})

				this.$editor.on('mousemove',function (e) {

					if (e.pageX !== oldX || e.pageY !== oldY) {
						shouldSetFocus = false
					}

				})

				this.$editor.on('click', function (e) {

					oldX = undefined
					oldY = undefined

					if (!shouldSetFocus) {
						return
					}

					var editorPosition = _this.$editor.offset()

					_this.setFocus({
						x: e.pageX - editorPosition.left,
						y: e.pageY - editorPosition.top
					})

					// 点击 editor 聚焦输入框
					_this.$editor.find('input[type=text]').focus()

				}).on('click', 'input', function () {
					if (!this.value) {
						_this.showHistoryTips()
					}
					return false
				})

			}

			/**
			 * 处理输入
			 * @param  {Boolean} submitByEnter Enter 键入
			 */
			MemberInput.prototype.bindInputFinished = function (submitByEnter) {
				
				var _this = this

				_this.$editor.on('blur', 'input', function () {

					inputFinished.call(this)

				}).on('input', 'input', function () {

					var value = this.value

					if (/[,;；、]/.test(value)) {
						inputFinished.call(this, true)
					}

				})

				function inputFinished (shouldContinue) {
					_this.inputFinished(this, shouldContinue)
				}

			}

			/**
			 * 删除处理
			 */
			MemberInput.prototype.bindDelete = function () {

				var _this = this

				_this.$editor.on('keydown', function (e) {

					switch (e.keyCode) {

						// 退格、删除
						case 8:
						case 46:
							if ($(e.target).is('input')) {

								var cursorStart = e.target.selectionStart
								var cursorEnd = e.target.selectionEnd
								var isDelete

								if (typeof cursorStart !== 'undefined') {
									isDelete = cursorStart === cursorEnd &&
											((cursorStart === 0 && e.keyCode === 8) ||
											(cursorStart === _this.$editor.find('input').val().length && e.keyCode === 46))
								} else {
									isDelete = !_this.$editor.find('input').val() &&
										(e.keyCode === 8 || e.keyCode === 46)
								}
								if (isDelete) {

									var direction
									if (e.keyCode === 8) {
										direction = 'prev'
									} else {
										direction = 'next'
									}

									_this.inputDelete(direction)
									return false

								} else {
									setTimeout(function () {
										if (!_this.$editor.find('input').val().length) {
											_this.hideTips()
										}
									}, 0)
								}
							} else {
								this.selectDelete()
							}
							break
						case 37:
						case 39:
							if ($(e.target).is('input')) {

								var cursorStart = e.target.selectionStart
								var cursorEnd = e.target.selectionEnd

								if (cursorStart === cursorEnd &&
									((cursorStart === 0 && e.keyCode === 37) ||
										(cursorStart === _this.$editor.find('input').val().length && e.keyCode === 39))) {
									var method
									if (e.keyCode === 37) {
										direction = 'left'
									} else {
										direction = 'right'
									}

									_this.setFocus({
										direction: direction
									})
									return false
								} else {
									setTimeout(function () {
										if (!_this.$editor.find('input').val().length) {
											_this.hideTips()
										}
									}, 0)
								}
							} else {
								_this.selectDelete()
							}
							break
					}

				})

			}

			/**
			 * 输入框动态调整尺寸
			 */
			MemberInput.prototype.bindInputSize = function () {

				var _this = this

				this.$editor.on('input', 'input', function (e) {

					_this.adjustInputSize(this.value.length)

				})

			}

			/**
			 * 处理粘贴操作
			 */
			MemberInput.prototype.bindPaste = function () {

				var _this = this

				this.$editor.on('paste', 'input', function (e) {

					this.value += ';'

				})

			}

			/**
			 * 原始输入框 change
			 */
			MemberInput.prototype.bindChange = function () {

				var _this = this

				this.$input.on('change', function () {

					var existValue = $(this).val().split(';')

					_this.reset()

					_this.setFocus({
						x: 0,
						y: 0
					})

					_this.$editor.find('input').val(existValue)
					_this.inputFinished(_this.$editor.find('input').get(), true)

				})

			}

			MemberInput.prototype.reset = function () {

				this.$editor.empty()
				this.memberPickerValue = []

			}

			// 绑定输入事件
			// 为了应对中文输入法带来的干扰，用了一个很变态的方法：
			// 在keyDown中绑定input事件，等input响应后立马解绑
			// 如果遇到中文输入法keyCode===229，则不绑定事件
			MemberInput.prototype.bindInputTips = function () {
				
				var _this = this

				function bindTextInput () {
					// keydown for Chrome/New Opera
					// keyup for Safari
					// input for Firefox
					_this.$editor.on('input.textinput input', 'input', function (e) {
						// console.log(e.type)
						// 过滤中文输入法产生的分词符号
						_this.showTips(this.value.replace(/['\+|\s+]/g,''))

						if (!options.$tips) {
							_this.$tips.css('left',_this.$editor.find('input').position().left)
						}

					})
				}

				function unbindTextInput () {
					_this.$editor.off('input.textinput')
				}

				_this.$editor.on('keydown', 'input', function (e) {
					// console.log(e.type)

					switch (e.keyCode) {

						// 上
						case 38:
							if (_this.$tips.is(':visible')) {
								_this.rollTips('prev')
							}
							return false
							break
						// 下
						case 40:
							if (_this.$tips.is(':visible')) {
								_this.rollTips('next')
							} else {
								if (!this.value) {
									_this.showHistoryTips()
								}
							}
							return false
							break

						// Tab、回车
						case 9:
						case 13:
							if (groupMailRegExp.test(this.value)) {
								var $input = _this.$editor.find('input')
								_this.inputFinished($input.get(0), true)
							}
							if (!e.metaKey && !e.ctrlKey) {
								if (_this.$tips.is(':visible')) {
									_this.selectTips()
								} else if (!this.value && options.submitByEnter) {
									options.onSubmit &&
											options.onSubmit(_this.memberPickerValue.join(';'))
								}
								return false
							}
							break

						case 27:
							 this.value = ''
							_this.hideTips()
							break
					}

					// 6月11日修改，中文输入法下也出现提示
					// if(e.keyCode !== 229){
						bindTextInput()
						setTimeout(unbindTextInput, 0)
					// }
				})

				_this.$tips.on('mousedown', 'li a', function (e) {
					_this.selectTips(_this.$tips.find('li a').index($(this)))
					return false
				})
			}

			/**
			 * 插入成员
			 * @param  {String} value 插入值
			 */
			MemberInput.prototype.appendValue = function (value) {
				this.setFocus({
					x:this.$editor.width(),
					y:this.$editor.height()
				})
				this.$editor.find('input').val(value)
				this.inputFinished(this.$editor.find('input').get(),true)
			}

			/**
			 * 获取输入值
			 * @param  {*} format         输入值格式
			 * @param  {String} delimiter 分隔符
			 */
			MemberInput.prototype.getValue = function (format, delimiter) {
				
				var _this = this

				if (!format) {
					format = 'string'
				}
				if (!delimiter) {
					delimiter = ';'
				}

				var ret

				switch (format) {
					case 'array':
						ret = _this.memberPickerValue.slice()
						break
					case 'json':
						ret = JSON.stringify(_this.memberPickerValue)
						break
					case 'string':
					default:
						ret = _this.memberPickerValue.join(delimiter)
						break
				}

				return ret

			}

			/**
			 * 移除组件
			 */
			MemberInput.prototype.remove = function () {

				this.$wrapper.remove()
				this.memberPickerValue = []

			}

			// 显示最近输入
			MemberInput.prototype.showHistoryTips = function () {

				var historyMemberArr = this.getHistory()
				if (!historyMemberArr.length) {
					return
				}

				this.tipsCount = historyMemberArr.length

				var tipsHtml = historyMemberArr.map(function (tipsItem) {
					return '<li><a href="javascript:;"><div class="avatar"><span style="background-image: url(http://dcloud.oa.com/Public/Avatar/' + tipsItem + '.png);"></span></div>' + tipsItem + '</a></li>'
				}).join('')

				this.$tips.show().find('ul').html(tipsHtml)

				this.rollTips(0)

			}

			// 将历史记录存入本地存储，以便后续获取
			MemberInput.prototype.setHistory = function (memberArr) {

				if (!window.localStorage) {
					return false
				}

				var targetMemberArr = memberArr.slice()

				if (targetMemberArr.length < 4) {
					// 如果小于4条，则与旧记录合并
					targetMemberArr = targetMemberArr.concat(this.getHistory())

				}

				targetMemberArr = targetMemberArr.filter(function (memberItem,index) {
					return index === targetMemberArr.lastIndexOf(memberItem)
				}).slice(0,options.maxTipsCount)

				localStorage.setItem('oaui_memberinput_history',JSON.stringify(targetMemberArr))

			}

			// 读取本地存储记录
			MemberInput.prototype.getHistory = function () {

				if (!window.localStorage) {
					return []
				}

				var historyMemberArr = JSON.parse(localStorage.getItem('oaui_memberinput_history') || '[]')

				return historyMemberArr

			}

			return $.each(this,function () {

				var $input = $(this)
				if (!$input.data('memberInput')) {
					$input.data('memberInput',new MemberInput($input))
				}

			})

		},

		/**
		 * 重置 memberInput
		 */
		memberReset: function () {
			return $.each(this, function () {

				var $this = $(this)
				var $memberInput = $this.data('memberInput')
				
				$memberInput.$input.val('')
				$memberInput.$editor.empty()
				$memberInput.memberPickerValue = []

				// window.localStorage.setItem('oaui_memberinput_history', '[]')
				
			})
		}

	})

})(jQuery)
