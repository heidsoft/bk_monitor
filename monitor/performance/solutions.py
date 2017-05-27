# -*- coding: utf-8 -*-
import json

from utils.query_cc import CCBiz
from utils.request_middlewares import get_request


class JobSolution(object):

    solution_type = "job"

    job_type_display_name = u"作业平台"

    def __init__(self, cc_biz_id, task_id, is_enabled=True,
                 solution_params_replace=""):
        self.is_enabled = is_enabled
        self.solution_params_replace = solution_params_replace
        self.task_id = task_id
        self.biz_id = cc_biz_id

    @staticmethod
    def task_list(cc_biz_id):
        task_info_list = CCBiz.task_list(cc_biz_id)
        return [{"id": task["id"], "text": task["name"]}
                for task in task_info_list]

    def gen_solution_config(self):
        config = {
            "job_app_id": str(self.biz_id),
            "job_task_id": str(self.task_id),
            "job_task_name": "",
            "retry": "on",
            "parms": "",
            "retry_time": "3",
            "retry_count": "1",
            "steps": "0"
        }
        # get step list detail
        task_detail = CCBiz.task_detail(self.biz_id, self.task_id)
        if not task_detail:
            return {}
        config["job_task_name"] = task_detail["name"]
        steps = task_detail["nmStepBeanList"]
        if self.solution_params_replace == "replace":
            for index, step in enumerate(steps):
                if step["type"] == 1:
                    config["param%s" % index] = ""
        config["steps"] = str(len(steps))
        params = {
            "is_enabled": self.is_enabled,
            "biz_id": self.biz_id,
            "creator": get_request().user.username,
            "solution_type": self.solution_type,
            "title": "",
            "config": json.dumps(config)
        }
        return params


class SolutionConf(object):

    solution_model_list = [
        JobSolution
    ]

    @classmethod
    def solution_model(cls, solution_type):
        for s in cls.solution_model_list:
            if getattr(s, "solution_type") == solution_type:
                return s
        return None

    @classmethod
    def get_solution_obj(cls, solution_type, cc_biz_id, task_id, **kwargs):
        _model = cls.solution_model(solution_type)
        if _model:
            return _model(cc_biz_id, task_id, **kwargs)

    @classmethod
    def solution_type_display_name(cls, solution_type):
        _model = cls.solution_model(solution_type)
        if not _model:
            return u"无效的任务类型"
        return getattr(_model, 'job_type_display_name', solution_type)