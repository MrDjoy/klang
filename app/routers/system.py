#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统管理API路由
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.database import get_db
from app.models.views import ResponseModel
from app.models.models import TradingPlan, MonitorTask

router = APIRouter()


@router.get("/health", response_model=ResponseModel)
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        async with get_db() as session:
            await session.execute(select(1))

        return ResponseModel(
            code=200,
            message="系统运行正常",
            data={
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统异常: {str(e)}")


@router.get("/status", response_model=ResponseModel)
async def get_system_status():
    """获取系统状态"""
    try:
        async with get_db() as session:
            # 获取统计数据
            total_plans = (await session.execute(select(TradingPlan))).scalars().count()
            active_tasks = (await session.execute(
                select(MonitorTask).where(MonitorTask.status == "running")
            )).scalars().count()
            stopped_tasks = (await session.execute(
                select(MonitorTask).where(MonitorTask.status == "stopped")
            )).scalars().count()

            # 获取最后执行时间
            last_run = (await session.execute(
                select(func.max(MonitorTask.last_run_time))
            )).scalar_one()

        return ResponseModel(
            code=200,
            message="success",
            data={
                "total_plans": total_plans,
                "active_tasks": active_tasks,
                "stopped_tasks": stopped_tasks,
                "last_monitor_time": last_run,
                "system_status": "running" if active_tasks > 0 else "idle",
                "server_time": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")


@router.get("/config", response_model=ResponseModel)
async def get_system_config():
    """获取系统配置信息"""
    try:
        import sys
        import platform
        import sqlite3
        from sqlalchemy import __version__ as sqlalchemy_version

        return ResponseModel(
            code=200,
            message="success",
            data={
                "python_version": sys.version,
                "platform": platform.platform(),
                "sqlite_version": sqlite3.sqlite_version,
                "sqlalchemy_version": sqlalchemy_version,
                "server_start_time": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")