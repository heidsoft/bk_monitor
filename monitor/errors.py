# -*- coding: utf-8 -*-
"""
@desc: 这里定义异常
"""

class Error(Exception):
    pass


class APIError(Error):
    pass


class ESBAPIError(APIError):
    pass


class CCAPIError(ESBAPIError):
    pass


class JOBAPIError(ESBAPIError):
    pass


class JAAPIError(APIError):
    pass


class JAItemDoseNotExists(JAAPIError):
    pass


class MessageTemplateSyntaxError(Error):
    pass

class TableNotExistException(Error):
    """数据平台结果表不存在
    """
    def __init__(self, message):
        self.message = getattr(message, "message", message)
        self.table_name = self.message.strip(u"结果表").strip(u"不存在")

    def __str__(self):
        return self.message


class SqlQueryException(Error):
    """数据平台sql查询异常
    """
    pass


class PermissionException(Error):
    """权限不足
    """
    pass


class EmptyQueryException(Error):
    """数据平台sql查询无数据
    """
    pass
