#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/11 18:09
@Author  : dingyi11@baidu.com
@File    : test
"""
from app.main import app
from fastapi.testclient import TestClient
from fastapi import status
from app.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 测试数据库配置（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

TestAsyncSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def override_get_db():
    """覆盖数据库会话"""
    async with TestAsyncSessionLocal() as session:
        try:
            print('🔥 Override: run override_get_db')
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()



client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db



def sample_trading_plan():
    """返回示例交易计划数据"""
    return {
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "buy_price": 10.5,
        "stop_loss_price": 9.5,
        "take_profit_price": 12.0,
        "quantity": 1000,
        "threshold": 0.01,
        "date_up_rate": 0.05,
        "date_down_rate": 0.03,
        "total_down_rate": 0.05
    }

def test_create_trading_plan():
    """测试创建交易计划"""
    print(f'开始跑测试用例test_create_trading_plan')
    response = client.post("/api/v1/trading-plans", json=sample_trading_plan())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["stock_code"] == sample_trading_plan()["stock_code"]