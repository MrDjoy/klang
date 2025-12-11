#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盯盘任务管理API路由
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.core.monitor_service import MonitorService
from sqlalchemy import select, delete

from app.database import get_db
from app.models.views import (
    MonitorTaskCreate, MonitorTaskResponse, ResponseModel
)
from app.models.models import (
    MonitorTask, TradingPlan, ExecutionLog
)

router = APIRouter()


@router.get("/monitor-tasks", response_model=ResponseModel)
async def get_monitor_tasks(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None
):
    """获取盯盘任务列表"""
    try:
        offset = (page - 1) * size
        async with get_db() as session:
            # 构建查询
            stmt = select(MonitorTask).join(TradingPlan)
            if status:
                stmt = stmt.where(MonitorTask.status == status)

            # 查询总数
            total = (await session.execute(select(MonitorTask))).scalars().count()

            # 查询数据
            stmt = stmt.order_by(MonitorTask.updated_at.desc()).limit(size).offset(offset)
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            # 转换为字典列表
            items = [{
                **task.__dict__,
                "stock_code": task.plan.stock_code,
                "stock_name": task.plan.stock_name
            } for task in tasks]

        return ResponseModel(
            code=200,
            message="success",
            data={
                "total": total,
                "page": page,
                "size": size,
                "items": items
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取盯盘任务失败: {str(e)}")
    finally:
        pass  # 异步会话会自动关闭


@router.post("/monitor-tasks", response_model=ResponseModel)
async def create_monitor_task(task: MonitorTaskCreate):
    """创建盯盘任务"""
    try:
        async with get_db() as session:
            # 检查交易计划是否存在
            stmt = select(TradingPlan).where(
                TradingPlan.id == task.trading_plan_id,
                TradingPlan.status == "enable"
            )
            result = await session.execute(stmt)
            plan = result.scalar_one_or_none()
            if not plan:
                raise HTTPException(status_code=404, detail="交易计划不存在或未启用")

            # 检查是否已存在监控任务
            stmt = select(MonitorTask).where(
                MonitorTask.trading_plan_id == task.trading_plan_id
            )
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="该交易计划已有监控任务")

            # 创建新记录
            db_task = MonitorTask(
                trading_plan_id=task.trading_plan_id,
                interval_minutes=task.interval_minutes,
                status=task.status
            )

            session.add(db_task)
            await session.commit()
            await session.refresh(db_task)

            # 获取关联数据
            new_task = {
                **db_task.__dict__,
                "stock_code": plan.stock_code,
                "stock_name": plan.stock_name
            }

        return ResponseModel(
            code=200,
            message="盯盘任务创建成功",
            data=dict(new_task)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建盯盘任务失败: {str(e)}")
    finally:
        pass

@router.post("/monitor-tasks/{task_id}/start", response_model=ResponseModel)
async def start_monitor_task(task_id: int):
    """启动盯盘任务"""
    try:
        async with get_db() as session:
            # 检查任务是否存在
            stmt = select(MonitorTask).where(MonitorTask.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()
            if not task:
                raise HTTPException(status_code=404, detail="盯盘任务不存在")

            if task.status == "running":
                raise HTTPException(status_code=400, detail="盯盘任务已在运行中")

            # 检查关联的交易计划是否启用
            stmt = select(TradingPlan).where(
                TradingPlan.id == task.trading_plan_id,
                TradingPlan.status == "enable"
            )
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="关联的交易计划未启用")

            # 更新任务状态和下次执行时间
            task.status = "running"
            task.next_run_time = datetime.now()
            await session.commit()

            # 通知监控服务
            await monitor_service.add_task(task_id)

        return ResponseModel(
            code=200,
            message="盯盘任务启动成功",
            data={"id": task_id, "status": "running"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动盯盘任务失败: {str(e)}")
    finally:
        pass

@router.post("/monitor-tasks/{task_id}/stop", response_model=ResponseModel)
async def stop_monitor_task(task_id: int):
    """停止盯盘任务"""
    try:
        async with get_db() as session:
            # 检查任务是否存在
            stmt = select(MonitorTask).where(MonitorTask.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()
            if not task:
                raise HTTPException(status_code=404, detail="盯盘任务不存在")

            if task.status == "stopped":
                raise HTTPException(status_code=400, detail="盯盘任务已停止")

            # 更新任务状态
            task.status = "stopped"
            task.next_run_time = None
            await session.commit()

            # 通知监控服务
            await monitor_service.remove_task(task_id)

        return ResponseModel(
            code=200,
            message="盯盘任务停止成功",
            data={"id": task_id, "status": "stopped"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止盯盘任务失败: {str(e)}")
    finally:
        pass


@router.get("/monitor-tasks/{task_id}/logs", response_model=ResponseModel)
async def get_monitor_task_logs(
    task_id: int,
    page: int = 1,
    size: int = 20
):
    """获取盯盘任务执行日志"""
    try:
        offset = (page - 1) * size
        async with get_db() as session:
            # 检查任务是否存在
            stmt = select(MonitorTask).where(MonitorTask.id == task_id)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="盯盘任务不存在")

            # 查询总数
            total = (await session.execute(
                select(ExecutionLog).where(ExecutionLog.task_id == task_id)
            )).scalars().count()

            # 查询日志数据
            stmt = (
                select(ExecutionLog)
                .where(ExecutionLog.task_id == task_id)
                .order_by(ExecutionLog.execution_time.desc())
                .limit(size)
                .offset(offset)
            )
            result = await session.execute(stmt)
            logs = result.scalars().all()

            # 转换为字典列表
            items = [log.__dict__ for log in logs]

        return ResponseModel(
            code=200,
            message="success",
            data={
                "total": total,
                "page": page,
                "size": size,
                "items": items
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控日志失败: {str(e)}")
    finally:
        pass


@router.delete("/monitor-tasks/{task_id}", response_model=ResponseModel)
async def delete_monitor_task(task_id: int):
    """删除盯盘任务"""
    try:
        async with get_db() as session:
            # 检查任务是否存在
            stmt = select(MonitorTask).where(MonitorTask.id == task_id)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="盯盘任务不存在")

            # 删除任务（关联的执行日志也会被删除）
            stmt = delete(MonitorTask).where(MonitorTask.id == task_id)
            await session.execute(stmt)
            await session.commit()

        return ResponseModel(
            code=200,
            message="盯盘任务删除成功",
            data={"id": task_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除盯盘任务失败: {str(e)}")
    finally:
        pass