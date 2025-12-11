import pytest
from fastapi import status
from app.main import app
from app.database import Base, get_db
from app.tests.conftest import override_get_db

class TestTradingPlansAPI:
    """交易计划API测试套件"""

    @pytest.mark.asyncio
    async def test_create_trading_plan(self, client, sample_trading_plan):
        """测试创建交易计划"""
        print(f'开始跑测试用例test_create_trading_plan')
        response = client.post("/api/v1/trading-plans", json=sample_trading_plan)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["stock_code"] == sample_trading_plan["stock_code"]


    # @pytest.mark.asyncio
    # async def test_create_duplicate_plan(self, client, sample_trading_plan):
    #     """测试创建重复股票代码的交易计划"""
    #     client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     response = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST
    #     assert "该股票代码的交易计划已存在" in response.json()["detail"]
    #
    # @pytest.mark.asyncio
    # async def test_get_trading_plan(self, client, sample_trading_plan):
    #     """测试获取单个交易计划"""
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     response = client.get(f"/api/v1/trading-plans/{plan_id}")
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["data"]["id"] == plan_id
    #
    # @pytest.mark.asyncio
    # async def test_get_nonexistent_plan(self, client):
    #     """测试获取不存在的交易计划"""
    #     response = client.get("/api/v1/trading-plans/999")
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_update_trading_plan(self, client, sample_trading_plan):
    #     """测试更新交易计划"""
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     update_data = sample_trading_plan.copy()
    #     update_data["buy_price"] = 11.0
    #
    #     response = client.put(f"/api/v1/trading-plans/{plan_id}", json=update_data)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["data"]["buy_price"] == 11.0
    #
    # @pytest.mark.asyncio
    # async def test_delete_trading_plan(self, client, sample_trading_plan):
    #     """测试删除交易计划"""
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     response = client.delete(f"/api/v1/trading-plans/{plan_id}")
    #     assert response.status_code == status.HTTP_200_OK
    #
    #     # 验证已删除
    #     get_response = client.get(f"/api/v1/trading-plans/{plan_id}")
    #     assert get_response.status_code == status.HTTP_404_NOT_FOUND
    #
    # @pytest.mark.asyncio
    # async def test_list_trading_plans(self, client, sample_trading_plan):
    #     """测试获取交易计划列表"""
    #     client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #
    #     response = client.get("/api/v1/trading-plans")
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.json()["data"]["items"]) > 0
    #
    # @pytest.mark.asyncio
    # async def test_update_plan_status(self, client, sample_trading_plan):
    #     """测试更新交易计划状态"""
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     # 禁用计划
    #     response = client.patch(
    #         f"/api/v1/trading-plans/{plan_id}/status",
    #         params={"status": "disable"}
    #     )
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["data"]["status"] == "disable"
    #
    # @pytest.mark.asyncio
    # async def test_invalid_status_update(self, client, sample_trading_plan):
    #     """测试无效状态更新"""
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     response = client.patch(
    #         f"/api/v1/trading-plans/{plan_id}/status",
    #         params={"status": "invalid"}
    #     )
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST
    #
    # @pytest.mark.asyncio
    # async def test_concurrent_queries(self, client, sample_trading_plan):
    #     """测试并发查询同一股票代码"""
    #     import asyncio
    #
    #     # 创建测试数据
    #     create_res = client.post("/api/v1/trading-plans", json=sample_trading_plan)
    #     plan_id = create_res.json()["data"]["id"]
    #
    #     # 并发查询
    #     async def query_plan():
    #         response = client.get(f"/api/v1/trading-plans/{plan_id}")
    #         assert response.status_code == status.HTTP_200_OK
    #         return response.json()
    #
    #     tasks = [query_plan() for _ in range(10)]
    #     results = await asyncio.gather(*tasks, return_exceptions=True)
    #
    #     # 验证所有查询都成功
    #     for result in results:
    #         if isinstance(result, Exception):
    #             raise result
    #         assert result["data"]["id"] == plan_id