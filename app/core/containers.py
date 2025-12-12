#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/12 11:23
@Author  : dingyi11@baidu.com
@File    : containers
"""
from dependency_injector import containers, providers
from .monitor_service import MonitorService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.routers.monitor_tasks"])
    monitor_service = providers.Singleton(MonitorService)