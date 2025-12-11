#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盯盘任务监控服务
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_async
from app.models.models import MonitorTask, TradingPlan, ExecutionLog, EmailConfig
from data.monitor import StockMonitor

logger = logging.getLogger(__name__)


class MonitorService:
    """盯盘任务监控服务"""

    def __init__(self):
        self._running = False
        self._tasks: Dict[int, asyncio.Task] = {}

    async def start(self):
        """启动监控服务"""
        if self._running:
            logger.warning("监控服务已在运行中")
            return

        self._running = True
        logger.info("启动监控服务")

        # 加载所有运行中的任务
        async with get_db_async() as session:
            stmt = select(MonitorTask).where(MonitorTask.status == "running")
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            for task in tasks:
                self._schedule_task(task)

    async def _schedule_task(self, task: MonitorTask):
        """安排定时任务"""
        if task.id in self._tasks:
            logger.warning(f"任务 {task.id} 已在运行中")
            return

        async def task_wrapper():
            """任务包装器，处理异常"""
            try:
                await self._execute_monitor_task(task)
            except Exception as e:
                logger.error(f"执行任务 {task.id} 失败: {e}")
            finally:
                if task.id in self._tasks:
                    del self._tasks[task.id]

        # 创建定时任务
        async def run_periodically():
            """定期执行任务"""
            while self._running and task.id in self._tasks:
                try:
                    await self._execute_monitor_task(task)
                    await asyncio.sleep(task.interval_minutes * 60)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"任务 {task.id} 执行出错: {e}")
                    await asyncio.sleep(60)  # 出错后等待1分钟再重试

        self._tasks[task.id] = asyncio.create_task(run_periodically())
        logger.info(f"已安排任务 {task.id}，每 {task.interval_minutes} 分钟执行一次")

    async def _execute_monitor_task(self, task: MonitorTask):
        """执行监控任务"""
        async with get_db_async() as session:
            # 获取任务最新数据
            stmt = select(MonitorTask).where(MonitorTask.id == task.id)
            result = await session.execute(stmt)
            task = result.scalar_one()

            # 检查任务是否仍处于运行状态
            if task.status != "running":
                logger.info(f"任务 {task.id} 已停止，取消执行")
                await self.remove_task(task.id)
                return

            # 获取关联的交易计划
            stmt = select(TradingPlan).where(TradingPlan.id == task.trading_plan_id)
            result = await session.execute(stmt)
            plan = result.scalar_one()

            # 创建监控实例
            email_config = await self._get_email_config(session)
            monitor = StockMonitor(email_config=email_config)

            # 设置交易计划
            monitor.set_trading_plan(
                code=plan.stock_code,
                buy_price=plan.buy_price,
                stop_loss_price=plan.stop_loss_price,
                take_profit_price=plan.take_profit_price,
                quantity=plan.quantity,
                threshold=plan.threshold,
                date_up_rate=plan.date_up_rate,
                date_down_rate=plan.date_down_rate,
                total_down_rate=plan.total_down_rate
            )

            # 执行监控
            logger.info(f"开始执行任务 {task.id} - {plan.stock_code}")
            await asyncio.to_thread(monitor.monitor_stocks)

            # 更新任务最后执行时间
            task.last_run_time = datetime.now()
            task.next_run_time = datetime.now() + timedelta(minutes=task.interval_minutes)
            await session.commit()

            # 记录执行日志
            log = ExecutionLog(
                task_id=task.id,
                stock_code=plan.stock_code,
                execution_time=datetime.now(),
                result="success",
                signal_type="none"
            )
            session.add(log)
            await session.commit()

    async def _get_email_config(self, session: AsyncSession) -> Dict:
        """获取邮件配置"""
        stmt = select(EmailConfig).order_by(EmailConfig.id.desc()).limit(1)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()
        return config.__dict__ if config else {}

    async def add_task(self, task_id: int):
        """添加新任务"""
        if not self._running:
            return

        async with get_db_async() as session:
            stmt = select(MonitorTask).where(MonitorTask.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one()

            if task.status == "running":
                self._schedule_task(task)

    async def remove_task(self, task_id: int):
        """移除任务"""
        if task_id in self._tasks:
            self._tasks[task_id].cancel()
            del self._tasks[task_id]
            logger.info(f"已取消任务 {task_id}")

    async def restart_task(self, task_id: int):
        """重启任务"""
        await self.remove_task(task_id)
        await self.add_task(task_id)

    async def stop(self):
        """停止监控服务"""
        if not self._running:
            logger.warning("监控服务未运行")
            return

        self._running = False
        logger.info("停止监控服务")

        # 取消所有任务
        for task_id, task in list(self._tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.debug(f"任务 {task_id} 已取消")
            except Exception as e:
                logger.error(f"取消任务 {task_id} 时出错: {e}")
            finally:
                del self._tasks[task_id]

        logger.info("所有监控任务已停止")