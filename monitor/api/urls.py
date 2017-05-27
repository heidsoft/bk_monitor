# -*- coding: utf-8 -*-
from django.conf.urls import patterns

api_urlpatterns = patterns(
    "monitor.api.data",
    (r"^api/trt/list_result_table_detail/$", "list_result_table_detail"),
    (r"^api/trt/list_datasets/$", "list_datasets"),
    (r"^api/trt/list_dataset_fields/$", "list_dataset_fields"),
)
