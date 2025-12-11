#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盯盘机器人Web应用 - 主入口文件
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import trading_plans, monitor_tasks, email_config, system
from app.database import init_db, get_db
from app.core.monitor_service import MonitorService
monitor_service = MonitorService()
from fastapi import Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi import applications

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

# def swagger_monkey_patch(*args,**kwargs):
#     return get_swagger_ui_html(*args, **kwargs,
#     # swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swaqqer-ui/5.6.2/swaqqer-ui-bundle.js",
#     # swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swaqqer-ui/5.6.2/swaqqer-ui.min.css")
#     swagger_js_url="https://petstore.swagger.io/swagger-ui-bundle.js",
#     swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css")
#
# applications.get_swagger_ui_html=swagger_monkey_patch

@asynccontextmanager
async def lifespan(appx: FastAPI):
    try:
        # 初始化数据库
        await init_db()
        # 启动监控服务
        await monitor_service.start()

        yield

        # 停止所有监控任务
        await monitor_service.stop()

    finally:
        pass


# 创建FastAPI应用
app = FastAPI(
    title="自动盯盘机器人Web应用",
    description="股票交易计划和盯盘任务管理Web应用",
    version="1.0.0",
    lifespan=lifespan
)

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

# @app.on_event("startup")
# async def startup_event():
#     """应用启动事件"""
#     # 初始化数据库
#     await init_db()
#
#     # 启动监控服务
#     await monitor_service.start()
#
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     """应用关闭事件"""
#     # 停止所有监控任务
#     await monitor_service.stop()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "自动盯盘机器人Web应用",
        "version": "1.0.0",
        "docs": "/docs",
        "api_base": "/api/v1"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )