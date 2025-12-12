#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盯盘机器人Web应用 - 主入口文件
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.containers import Container
from app.routers import trading_plans, monitor_tasks, email_config, system
from app.database import init_db
from fastapi import Depends

from contextlib import asynccontextmanager

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # 初始化数据库
        await init_db()
        # 启动监控服务
        await app.container.monitor_service().start()

        yield

        # 停止所有监控任务
        await app.container.monitor_service().stop()

    finally:
        pass


def create_app() -> FastAPI:
    container = Container()

    # 创建FastAPI应用
    app = FastAPI(
        title="自动盯盘机器人Web应用",
        description="股票交易计划和盯盘任务管理Web应用",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.container = container

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载静态文件目录
    # app.mount("/static", StaticFiles(directory="dist"), name="static")

    # 注册路由
    app.include_router(
        trading_plans.router,
        prefix="/api/v1",
        tags=["交易计划管理"]
    )
    app.include_router(
        monitor_tasks.router,
        prefix="/api/v1",
        tags=["盯盘任务管理"]
    )
    app.include_router(
        email_config.router,
        prefix="/api/v1",
        tags=["邮件配置管理"]
    )
    app.include_router(
        system.router,
        prefix="/api/v1",
        tags=["系统管理"]
    )

    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "自动盯盘机器人Web应用",
            "version": "1.0.0",
            "docs": "/docs",
            "api_base": "/api/v1"
        }

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )