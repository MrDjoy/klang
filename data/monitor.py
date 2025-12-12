#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/10 09:55
@Author  : dingyi11@baidu.com
@File    : monitor
"""
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
自动盯盘机器人模块
"""

import time
import smtplib
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from datetime import datetime
from typing import Dict, List
from data.trade_data import realtime_data
import pandas as pd

class StockMonitor:
    """股票盯盘机器人"""

    def __init__(self, email_config: Dict = None):
        """
        初始化盯盘机器人

        Args:
            email_config: 邮件配置字典，包含以下键：
                - smtp_server: SMTP服务器地址
                - smtp_port: SMTP端口
                - sender_email: 发送者邮箱
                - sender_password: 发送者密码
                - receiver_email: 接收者邮箱
        """
        self.trading_plans = {}  # 存储交易计划
        self.email_config = email_config or {}

    def set_trading_plan(self, code: str, buy_price: float, stop_loss_price: float,
                         take_profit_price: float, quantity: int, threshold: float = 0.01,
                         date_up_rate: float = 0.08, date_down_rate: float = 0.05,
                         total_down_rate: float = 0.05):
        """
        设置交易计划

        Args:
            code: 股票代码或名称
            buy_price: 买入价格
            stop_loss_price: 止损价格
            take_profit_price: 止盈价格
            quantity: 购买股数
            threshold: 价格阈值(默认1%)
            date_up_rate: 日涨幅超过百分比 (最新价格 - 开盘价格) / 开盘价格
            date_down_rate: 日跌幅超过百分比 (开盘价格 - 最新价格) / 开盘价格
            total_down_rate: 总跌幅百分比 (买入价格 - 最新价格) / 买入价格
        """
        self.trading_plans[code] = {
            'buy_price': buy_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'quantity': quantity,
            'threshold': threshold,
            'date_up_rate': date_up_rate,
            'date_down_rate': date_down_rate,
            'total_down_rate':total_down_rate,
        }
        print(f"已设置 {code} 的交易计划")

    def get_latest_price(self, code: str) -> float:
        """
        获取股票最新价格

        Args:
            code: 股票代码或名称

        Returns:
            最新价格
        """
        try:
            df = realtime_data(code=[code])
            if not df.empty:
                return float(df['最新'].iloc[0])
            return 0.0
        except Exception as e:
            print(f"获取 {code} 最新价格失败: {e}")
            return 0.0

    def get_realtime_stock(self, code: str) -> pd.DataFrame:
        try:
            df = realtime_data(code=[code])
            if not df.empty:
                return df
            return pd.DataFrame({})
        except Exception as e:
            print(f"获取 {code} 最新股票数据失败: {e}")
            return pd.DataFrame({})

    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_email(self, subject: str, content: str):
        """
        发送邮件通知

        Args:
            subject: 邮件主题
            content: 邮件内容
        """
        if not self.email_config:
            print("未配置邮件信息，仅打印通知：", content)
            return

        try:
            # 创建邮件对象
            message = MIMEMultipart()
            message['From'] = formataddr((Header(self.email_config.get('sender_name', '盯盘机器人'), 'utf-8').encode(),
                                          self.email_config['sender_email']))
            message['To'] = formataddr((Header(self.email_config.get('receiver_name', '用户'), 'utf-8').encode(),
                                        self.email_config['receiver_email']))
            message['Subject'] = Header(subject, 'utf-8')

            # 添加邮件正文
            message.attach(MIMEText(content, 'plain', 'utf-8'))

            # 连接SMTP服务器并发送邮件
            smtp_server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            smtp_server.starttls()
            smtp_server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            smtp_server.sendmail(self.email_config['sender_email'],
                                 self.email_config['receiver_email'],
                                 message.as_string())
            smtp_server.quit()
            print(f"邮件发送成功: {subject}")
        except Exception as e:
            print(f"邮件发送失败: {e}")

    def check_buy_signal(self, code: str, latest_price: float, plan: Dict) -> bool:
        """
        检查是否触发买入信号

        Args:
            code: 股票代码
            latest_price: 最新价格
            plan: 交易计划

        Returns:
            是否触发买入信号
        """
        buy_price = plan['buy_price']
        threshold = plan['threshold']

        # 判断最新价是否在买入价格的+-阈值范围内
        lower_bound = buy_price * (1 - threshold)
        upper_bound = buy_price * (1 + threshold)

        if lower_bound <= latest_price <= upper_bound:
            content = f"""
            【买入信号】{code}
            当前价格: {latest_price}
            买入价: {buy_price}
            数量: {plan['quantity']}股
            时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            self.send_email(f"【买入信号】{code}", content.strip())
            return True
        return False

    def check_stop_loss_signal(self, code: str, st_data: pd.DataFrame, plan: Dict) -> bool:
        """
        检查是否触发止损信号

        Args:
            code: 股票代码
            st_data: 最新价格
            plan: 交易计划

        Returns:
            是否触发止损信号
        """
        stop_loss_price = plan['stop_loss_price']
        date_down_rate = plan['date_down_rate']
        total_down_rate = plan['total_down_rate']
        buy_price = plan['buy_price']
        latest_price = st_data['最新'].iloc[0]
        open_price = st_data['今开'].iloc[0]
        high_price = st_data['最高'].iloc[0]
        low_price = st_data['最低'].iloc[0]
        up_down_rate = st_data['涨幅'].iloc[0]
        y_close_price = st_data['昨收'].iloc[0]
        name = st_data['名称'].iloc[0]

        # 当日跌幅 相对昨天
        df = (y_close_price - latest_price) / y_close_price
        # 当前亏损
        total_down = (buy_price - latest_price) / buy_price
        # 累计盈亏
        rate = (latest_price - buy_price) / buy_price

        # print(f'df:{df} date_down_rate:{date_down_rate} up_down_rate:{up_down_rate}')

        reason = ()
        if latest_price <= stop_loss_price:
            reason = (1, f'当前价格已低于止损价格{stop_loss_price}')
        elif df >= date_down_rate:
            reason = (2, f'当日跌幅已达到止损阈值{date_down_rate * 100}%')
        elif total_down >= total_down_rate:
            reason = (3, f'累计亏损已达到止损阈值{total_down_rate * 100}%')

        if not reason:
            return False

        content = f"""
        【止损信号】
        {name}{code}
        止损理由: {reason[1]}
        当前价格: {latest_price}
        开盘: {open_price}
        最高: {high_price}
        最低: {low_price}
        当日涨跌幅: {up_down_rate}%
        止损价格: {stop_loss_price}
        买入价: {buy_price}
        购买股数: {plan['quantity']}股
        浮动盈亏: {rate*100:.2f}% {plan['quantity'] * (latest_price - buy_price):.2f}
        时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.send_email(f"【止损信号】{name}{code}", content.strip())
        return True

    def check_take_profit_signal(self, code: str, st_data: pd.DataFrame, plan: Dict) -> bool:
        """
        检查是否触发止盈信号

        Args:
            code: 股票代码
            st_data: 最新价格
            plan: 交易计划

        Returns:
            是否触发止盈信号
        """
        take_profit_price = plan['take_profit_price']
        buy_price = plan['buy_price']
        date_up_rate = plan['date_up_rate']
        latest_price = st_data['最新'].iloc[0]
        open_price = st_data['今开'].iloc[0]
        high_price = st_data['最高'].iloc[0]
        low_price = st_data['最低'].iloc[0]
        up_down_rate = st_data['涨幅'].iloc[0]
        y_close_price = st_data['昨收'].iloc[0]
        name = st_data['名称'].iloc[0]

        # 当日涨幅
        zf = (latest_price - y_close_price) / y_close_price

        rate = (latest_price - buy_price) / buy_price if latest_price > buy_price \
            else (buy_price - latest_price) / buy_price
        reason = ()
        if latest_price >= take_profit_price:
            reason = (1, f'当前价格已达到止盈价格{take_profit_price}')
        elif zf >= date_up_rate:
            reason = (2, f'当日涨幅已达到止盈阈值{date_up_rate * 100}%')

        if not reason:
            return False

        content = f"""
        【止盈信号】
        {name}{code}
        止盈理由: {reason[1]}
        当前价格: {latest_price}
        开盘: {open_price}
        最高: {high_price}
        最低: {low_price}
        当日涨跌幅: {up_down_rate}%
        止盈价格: {take_profit_price}
        买入价: {buy_price}
        购买股数: {plan['quantity']}股
        浮动盈亏: {rate*100:.2f}% {plan['quantity'] * (latest_price - buy_price):.2f}
        时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.send_email(f"【止盈信号】{code}", content.strip())
        return True

    def monitor_stocks(self):
        """
        监控所有设置的股票
        """
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始本轮监控...")

        for code, plan in self.trading_plans.items():
            st_data = self.get_realtime_stock(code)
            latest_price = st_data['最新'].iloc[0]
            open_price = st_data['今开'].iloc[0]
            high_price = st_data['最高'].iloc[0]
            low_price = st_data['最低'].iloc[0]
            up_down_rate = st_data['涨幅'].iloc[0]

            if latest_price == 0.0:
                continue

            print(f"{code} 当前价格: {latest_price}")

            # 检查各种信号
            # self.check_buy_signal(code, latest_price, plan)
            self.check_stop_loss_signal(code, st_data, plan)
            self.check_take_profit_signal(code, st_data, plan)

    def start_monitoring(self, interval_minutes: int = 15):
        """
        开始定时监控

        Args:
            interval_minutes: 监控间隔(分钟)，默认5分钟
        """
        # 立即执行一次
        self.monitor_stocks()

        # 设置定时任务
        schedule.every(interval_minutes).minutes.do(self.monitor_stocks)

        print(f"已启动定时监控，每{interval_minutes}分钟检查一次")
        print("按 Ctrl+C 停止监控")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n监控已停止")


# 使用示例
if __name__ == "__main__":
    # 邮件配置示例（请根据实际情况修改）
    email_config = {
        'smtp_server': 'smtp.qq.com',  # SMTP服务器
        'smtp_port': 587,  # SMTP端口
        'sender_email': 'your@qq.com',  # 发送者邮箱
        'sender_password': 'yourpassword',  # 发送者授权码
        'receiver_email': 'receiver@qq.com',  # 接收者邮箱
        'sender_name': '盯盘机器人',  # 发送者名称
        'receiver_name': '投资者'  # 接收者名称
    }

    # 创建盯盘机器人实例
    # monitor = StockMonitor(email_config)  # 启用邮件通知
    monitor = StockMonitor()  # 不启用邮件通知，仅控制台输出

    # 设置交易计划
    # monitor.set_trading_plan(
    #     code='603162',  # 股票名称或代码
    #     buy_price=13.58,  # 买入价格
    #     stop_loss_price=12,  # 止损价格
    #     take_profit_price=14,  # 止盈价格
    #     quantity=800,  # 购买股数
    #     threshold=0.01,  # 价格阈值1%
    #     date_down_rate=0.04,  # 当日止损阈值2%
    #     total_down_rate=0.04  # 持仓亏损阈值4%
    # )
    # monitor.set_trading_plan(
    #     code='002046',  # 股票名称或代码
    #     buy_price=32.57,  # 买入价格
    #     stop_loss_price=30,  # 止损价格
    #     take_profit_price=35,  # 止盈价格
    #     quantity=200,  # 购买股数
    #     threshold=0.01  # 价格阈值1%
    # )
    monitor.set_trading_plan(
        code='603338',  # 股票名称或代码
        buy_price=60.726,  # 买入价格
        stop_loss_price=30,  # 止损价格
        take_profit_price=70,  # 止盈价格
        quantity=200,  # 购买股数
        threshold=0.0,  # 价格阈值1%
        date_down_rate=0.04,  # 当日止损阈值2%
        total_down_rate=0.04,  # 持仓亏损阈值4%
        date_up_rate=0.03  # 当日止盈阈值3%
    )

    # 启动监控（每5分钟检查一次）
    monitor.start_monitoring(15)