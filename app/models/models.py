#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLAlchemy 2.0 ORM模型定义
"""
from datetime import datetime, time
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, BigInteger, Time
)
from sqlalchemy.orm import relationship
from app.database import Base

class TradingPlan(Base):
    """交易计划模型"""
    __tablename__ = "trading_plans"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100), nullable=False)
    buy_price = Column(Float(precision=10, decimal_return_scale=2), nullable=False)
    stop_loss_price = Column(Float(precision=10, decimal_return_scale=2), nullable=False)
    take_profit_price = Column(Float(precision=10, decimal_return_scale=2), nullable=False)
    quantity = Column(Integer, nullable=False)
    threshold = Column(Float(precision=5, decimal_return_scale=2), default=0.01)
    date_up_rate = Column(Float(precision=5, decimal_return_scale=2), default=0.03)
    date_down_rate = Column(Float(precision=5, decimal_return_scale=2), default=0.04)
    total_down_rate = Column(Float(precision=5, decimal_return_scale=2), default=0.04)
    status = Column(String(10), default="enable")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("MonitorTask", back_populates="plan", cascade="all, delete")

class MonitorTask(Base):
    """盯盘任务模型"""
    __tablename__ = "monitor_tasks"

    id = Column(Integer, primary_key=True, index=True)
    trading_plan_id = Column(Integer, ForeignKey("trading_plans.id", ondelete="CASCADE"))
    interval_minutes = Column(Integer, nullable=False)
    last_run_time = Column(DateTime)
    next_run_time = Column(DateTime)
    status = Column(String(10), default="stopped")
    start_time = Column(Time, default=time(9, 30))  # 默认9:30开盘时间
    end_time = Column(Time, default=time(15, 0))    # 默认15:00收盘时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("TradingPlan", back_populates="tasks")
    logs = relationship("ExecutionLog", back_populates="task", cascade="all, delete")

class EmailConfig(Base):
    """邮件配置模型"""
    __tablename__ = "email_configs"

    id = Column(Integer, primary_key=True, index=True)
    smtp_server = Column(String(100), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    sender_email = Column(String(100), nullable=False)
    sender_password = Column(String(200), nullable=False)
    receiver_email = Column(String(100), nullable=False)
    sender_name = Column(String(100), default="盯盘机器人")
    receiver_name = Column(String(100), default="投资者")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionLog(Base):
    """执行日志模型"""
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("monitor_tasks.id", ondelete="CASCADE"))
    stock_code = Column(String(20), nullable=False)
    execution_time = Column(DateTime, nullable=False)
    result = Column(String(20), nullable=False)
    signal_type = Column(String(20), default="none")
    latest_price = Column(Float(precision=10, decimal_return_scale=2))
    open_price = Column(Float(precision=10, decimal_return_scale=2))
    high_price = Column(Float(precision=10, decimal_return_scale=2))
    low_price = Column(Float(precision=10, decimal_return_scale=2))
    volume = Column(BigInteger)
    change_rate = Column(Float(precision=5, decimal_return_scale=2))
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("MonitorTask", back_populates="logs")