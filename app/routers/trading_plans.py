#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交易计划管理API路由
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update, delete

from app.database import get_db
from app.models.models import (
    TradingPlan
)
from app.models.data_models import (
    ResponseModel, TradingPlanCreate, TradingPlanUpdate,
    TradingPlanResponse, PaginationParams, PaginatedResponse
)

router = APIRouter()


@router.get("/trading-plans", response_model=ResponseModel)
async def get_trading_plans(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None
):
    """获取交易计划列表"""
    try:
        offset = (page - 1) * size
        async with get_db() as session:
            # 构建查询
            stmt = select(TradingPlan)
            if status:
                stmt = stmt.where(TradingPlan.status == status)

            # 查询总数
            total = (await session.execute(select(TradingPlan))).scalars().count()

            # 查询数据
            stmt = stmt.order_by(TradingPlan.updated_at.desc()).limit(size).offset(offset)
            result = await session.execute(stmt)
            plans = result.scalars().all()

            # 转换为字典列表
            items = [plan.__dict__ for plan in plans]

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
        raise HTTPException(status_code=500, detail=f"获取交易计划失败: {str(e)}")
    finally:
        pass  # 异步会话会自动关闭


@router.get("/trading-plans/{plan_id}", response_model=ResponseModel)
async def get_trading_plan(plan_id: int):
    """获取单个交易计划"""
    try:
        async with get_db() as session:
            stmt = select(TradingPlan).where(TradingPlan.id == plan_id)
            result = await session.execute(stmt)
            plan = result.scalar_one_or_none()

            if not plan:
                raise HTTPException(status_code=404, detail="交易计划不存在")

        return ResponseModel(
            code=200,
            message="success",
            data=dict(plan)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易计划失败: {str(e)}")

    finally:
        pass


@router.post("/trading-plans", response_model=ResponseModel)
async def create_trading_plan(plan: TradingPlanCreate):
    """创建交易计划"""
    try:
        async with get_db() as session:
            # 检查股票代码是否已存在
            stmt = select(TradingPlan).where(TradingPlan.stock_code == plan.stock_code)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="该股票代码的交易计划已存在")

            # 创建新记录
            db_plan = TradingPlan(
                stock_code=plan.stock_code,
                stock_name=plan.stock_name,
                buy_price=plan.buy_price,
                stop_loss_price=plan.stop_loss_price,
                take_profit_price=plan.take_profit_price,
                quantity=plan.quantity,
                threshold=plan.threshold,
                date_up_rate=plan.date_up_rate,
                date_down_rate=plan.date_down_rate,
                total_down_rate=plan.total_down_rate,
                status=plan.status
            )

            session.add(db_plan)
            await session.commit()
            await session.refresh(db_plan)

        return ResponseModel(
            code=200,
            message="交易计划创建成功",
            data=db_plan.__dict__
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建交易计划失败: {str(e)}")

    finally:
        pass

@router.put("/trading-plans/{plan_id}", response_model=ResponseModel)
async def update_trading_plan(plan_id: int, plan: TradingPlanUpdate):
    """更新交易计划"""
    try:
        async with get_db() as session:
            # 检查计划是否存在
            stmt = select(TradingPlan).where(TradingPlan.id == plan_id)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="交易计划不存在")

            # 检查股票代码是否被其他计划使用
            stmt = select(TradingPlan).where(
                TradingPlan.stock_code == plan.stock_code,
                TradingPlan.id != plan_id
            )
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="该股票代码已被其他计划使用")

            # 更新记录
            stmt = (
                update(TradingPlan)
                .where(TradingPlan.id == plan_id)
                .values(
                    stock_code=plan.stock_code,
                    stock_name=plan.stock_name,
                    buy_price=plan.buy_price,
                    stop_loss_price=plan.stop_loss_price,
                    take_profit_price=plan.take_profit_price,
                    quantity=plan.quantity,
                    threshold=plan.threshold,
                    date_up_rate=plan.date_up_rate,
                    date_down_rate=plan.date_down_rate,
                    total_down_rate=plan.total_down_rate,
                    status=plan.status,
                    updated_at=datetime.now()
                )
            )
            await session.execute(stmt)
            await session.commit()

            # 获取更新后的记录
            stmt = select(TradingPlan).where(TradingPlan.id == plan_id)
            result = await session.execute(stmt)
            updated_plan = result.scalar_one()

        return ResponseModel(
            code=200,
            message="交易计划更新成功",
            data=dict(updated_plan)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新交易计划失败: {str(e)}")
    finally:
        pass


@router.delete("/trading-plans/{plan_id}", response_model=ResponseModel)
async def delete_trading_plan(plan_id: int):
    """删除交易计划"""
    try:
        async with get_db() as session:
            # 检查计划是否存在
            stmt = select(TradingPlan).where(TradingPlan.id == plan_id)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="交易计划不存在")

            # 删除记录（由于外键约束，关联的盯盘任务也会被删除）
            stmt = delete(TradingPlan).where(TradingPlan.id == plan_id)
            await session.execute(stmt)
            await session.commit()

        return ResponseModel(
            code=200,
            message="交易计划删除成功",
            data={"id": plan_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除交易计划失败: {str(e)}")
    finally:
        pass


@router.patch("/trading-plans/{plan_id}/status", response_model=ResponseModel)
async def update_trading_plan_status(plan_id: int, status: str):
    """启用/禁用交易计划"""
    try:
        if status not in ["enable", "disable"]:
            raise HTTPException(status_code=400, detail="状态必须是 enable 或 disable")

        async with get_db() as session:
            # 检查计划是否存在
            stmt = select(TradingPlan).where(TradingPlan.id == plan_id)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="交易计划不存在")

            # 更新状态
            stmt = (
                update(TradingPlan)
                .where(TradingPlan.id == plan_id)
                .values(status=status, updated_at=datetime.now())
            )
            await session.execute(stmt)
            await session.commit()

        return ResponseModel(
            code=200,
            message=f"交易计划已{status}",
            data={"id": plan_id, "status": status}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新状态失败: {str(e)}")
    finally:
        pass