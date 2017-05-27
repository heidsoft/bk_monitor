# -*- coding: utf-8 -*-
"""
用于本地开发环境的全局配置
"""
from settings import APP_ID
# API_URL = "http://139.199.155.22:8832"

# ===============================================================================
# 数据库设置, 本地开发数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': 'bk_monitor',                        # 数据库名 (默认与APP_ID相同)
        'USER': 'root',                        # 你的数据库user
        'PASSWORD': '123456',                        # 你的数据库password
        'HOST': 'localhost',                   # 开发的时候，使用localhost
        'PORT': '3306',                        # 默认3306
    },
}
