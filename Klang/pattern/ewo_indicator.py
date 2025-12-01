import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

class ElliottWaveOscillator:
    def __init__(self, fast_period: int = 5, slow_period: int = 34, ma_type: str = 'sma',
                 signal_period: int = 13, threshold: float = 0):
        """
        初始化EWO指标
        :param fast_period: 快速均线周期(默认5)
        :param slow_period: 慢速均线周期(默认34)
        :param ma_type: 均线类型('sma'/'ema'/'wma'等)
        :param signal_period: 信号线周期(默认13)
        :param threshold: 强度阈值
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.ma_type = ma_type.lower()
        self.signal_period = signal_period
        self.threshold = threshold

    def calculate_ma(self, series: pd.Series, period: int) -> pd.Series:
        """计算指定类型的移动平均"""
        if self.ma_type == 'sma':
            return series.rolling(window=period).mean()
        elif self.ma_type == 'ema':
            return series.ewm(span=period, adjust=False).mean()
        elif self.ma_type == 'wma':
            weights = np.arange(1, period+1)
            return series.rolling(window=period).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)
        else:
            raise ValueError("不支持的均线类型")

    def calculate_ewo(self, close_prices: pd.Series) -> pd.Series:
        """
        计算EWO指标
        :param close_prices: 收盘价序列(pandas.Series)
        :return: EWO值(pandas.Series)
        """
        fast_ma = self.calculate_ma(close_prices, self.fast_period)
        slow_ma = self.calculate_ma(close_prices, self.slow_period)
        ewo = fast_ma - slow_ma
        return ewo

    def calculate_signal_line(self, ewo_values: pd.Series) -> pd.Series:
        """
        计算EWO信号线(EWO的移动平均)
        :param ewo_values: EWO值序列
        :return: 信号线序列
        """
        return self.calculate_ma(ewo_values, self.signal_period)

    def generate_signals(self, close_prices: pd.Series) -> Dict[str, pd.Series]:
        """
        生成交易信号
        :param close_prices: 收盘价序列
        :return: 包含各种信号的字典
        """
        ewo = self.calculate_ewo(close_prices)
        signal_line = self.calculate_signal_line(ewo)

        # 信号定义
        signals = {
            'ewo': ewo,
            'signal_line': signal_line,
            'strong_long': (ewo > signal_line) & (ewo < -self.threshold),
            'long': (ewo > signal_line) & (ewo <= -self.threshold),
            'strong_short': (ewo < signal_line) & (ewo > self.threshold),
            'short': (ewo < signal_line) & (ewo <= self.threshold),
            'crossover': ewo > signal_line,
            'crossunder': ewo < signal_line
        }

        return signals

    def backtest_signals(self, data: pd.DataFrame, initial_capital: float = 1000.0) -> Dict:
        """
        简单的回测功能
        :param data: 包含价格和信号的数据
        :param initial_capital: 初始资金
        :return: 回测结果
        """
        if 'signal_line' not in data.columns:
            data['signals'] = self.generate_signals(data['close'])
            data = pd.concat([data, pd.DataFrame(data['signals'].tolist())], axis=1)

        capital = initial_capital
        position = 0
        trades = []

        for i in range(len(data)):
            if data['crossover'].iloc[i] and position <= 0:
                # 买入信号
                if position < 0:
                    # 平空仓
                    capital *= (data['close'].iloc[i] / data['close'].iloc[i-1])
                    position = 0
                # 开多仓
                position = 1
                trades.append({
                    'date': data.index[i],
                    'action': 'BUY',
                    'price': data['close'].iloc[i],
                    'capital': capital
                })

            elif data['crossunder'].iloc[i] and position >= 0:
                # 卖出信号
                if position > 0:
                    # 平多仓
                    capital *= (data['close'].iloc[i] / data['close'].iloc[i-1])
                    position = 0
                # 开空仓
                position = -1
                trades.append({
                    'date': data.index[i],
                    'action': 'SELL',
                    'price': data['close'].iloc[i],
                    'capital': capital
                })

        # 最终统计
        if position != 0:
            # 平掉最后持仓
            capital *= (data['close'].iloc[-1] / data['close'].iloc[-2])

        total_return = (capital - initial_capital) / initial_capital * 100

        return {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return_percent': total_return,
            'num_trades': len(trades),
            'trades': trades
        }

# 使用示例
def example_usage():
    # 创建示例数据
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)

    data = pd.DataFrame({'close': prices}, index=dates)

    # 创建EWO指标实例
    ewo_indicator = ElliottWaveOscillator(
        fast_period=5,
        slow_period=34,
        ma_type='ema',
        signal_period=13,
        threshold=0.1
    )

    # 生成信号
    signals = ewo_indicator.generate_signals(data['close'])

    # 将信号添加到数据中
    for key, values in signals.items():
        data[key] = values

    # 显示最新信号
    print("最新交易信号:")
    print(f"EWO值: {data['ewo'].iloc[-1]:.4f}")
    print(f"信号线: {data['signal_line'].iloc[-1]:.4f}")

    if data['strong_long'].iloc[-1]:
        print("信号类型: 强买入信号")
    elif data['long'].iloc[-1]:
        print("信号类型: 买入信号")
    elif data['strong_short'].iloc[-1]:
        print("信号类型: 强卖出信号")
    elif data['short'].iloc[-1]:
        print("信号类型: 卖出信号")
    else:
        print("信号类型: 持仓")

    # 运行回测
    backtest_results = ewo_indicator.backtest_signals(data)
    print(f"\n回测结果:")
    print(f"初始资金: {backtest_results['initial_capital']:.2f}")
    print(f"最终资金: {backtest_results['final_capital']:.2f}")
    print(f"总收益率: {backtest_results['total_return_percent']:.2f}%")
    print(f"交易次数: {backtest_results['num_trades']}")

    return data, ewo_indicator, backtest_results

if __name__ == "__main__":
    example_usage()
