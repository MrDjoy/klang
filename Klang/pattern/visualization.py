"""
K线可视化模块 - 直接在项目中绘制图表
"""

import numpy as np
from .zigzag_lib import peak_valley_pivots_np
from .patterns import create_index, pattern_cup_handle


class KlineVisualizer:
    """K线可视化器 - 直接在项目中绘制图表"""

    def __init__(self):
        self.cup_handle_results = None
        self.close_prices = None
        self.data = None
        self.pivots = None
        self.pv_index = None

    def analyze_data(self, data):
        """分析数据并检测模式"""
        self.data = data
        self.close_prices = data['close'].values

        # 检测转折点
        self.pivots = peak_valley_pivots_np(self.close_prices, step=10)
        self.pv_index = create_index(self.pivots)

        # 检测杯柄模式
        self.cup_handle_results = []
        if len(self.pv_index) >= 6:
            for i in range(len(self.pv_index)-5):
                pattern_result = self._check_cup_handle_at_position(i)
                if pattern_result['detected']:
                    self.cup_handle_results.append(pattern_result)

        return self._generate_analysis_report()

    def _check_cup_handle_at_position(self, start_idx):
        """检查指定位置是否存在杯柄模式"""
        if start_idx + 5 >= len(self.pv_index):
            return {'detected': False}

        idx_list = [self.pv_index[start_idx + j] for j in range(6)]
        a, b, c, d = idx_list[1], idx_list[2], idx_list[3], idx_list[4]

        # 检查杯柄模式条件
        ab = self.close_prices[a] - self.close_prices[b]
        cb = self.close_prices[c] - self.close_prices[b]
        cd = self.close_prices[c] - self.close_prices[d]

        detected = (self.pivots[a] == 1 and self.pivots[b] == -1 and
                   self.pivots[c] == 1 and abs(ab-cb)/cb < 0.15 and
                   self.close_prices[b] < self.close_prices[d] and cb/3 > cd)

        return {
            'detected': detected,
            'positions': idx_list,
            'points': {
                'A': (a, self.close_prices[a]),
                'B': (b, self.close_prices[b]),
                'C': (c, self.close_prices[c]),
                'D': (d, self.close_prices[d])
            }
        }

    def _generate_analysis_report(self):
        """生成分析报告"""
        report = {
            'summary': {
                'data_points': len(self.close_prices),
                'pivot_points': len(self.pv_index),
                'cup_handle_patterns': len(self.cup_handle_results)
            },
            'pivots': [],
            'patterns': []
        }

        # 转折点信息
        for idx in self.pv_index:
            report['pivots'].append({
                'index': idx,
                'price': float(self.close_prices[idx]),
                'type': 'peak' if self.pivots[idx] == 1 else 'valley'
            })

        # 杯柄模式信息
        for pattern in self.cup_handle_results:
            report['patterns'].append({
                'positions': pattern['positions'],
                'points': pattern['points']
            })

        return report

    def plot_kline(self, figsize=(12, 6)):
        """直接绘制K线图"""
        if self.data is None or self.data.empty:
            raise ValueError("请先调用 analyze_data() 方法分析数据")

        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=figsize)
        dates = range(len(self.close_prices))

        # 1. 绘制收盘价线
        # print(self.data['datetime'].values.ravel())
        sns.lineplot(x= self.data.index, y = self.close_prices.ravel(), label='close', linewidth=1)

        # 2. 标记转折点
        peak_indices = [idx for idx in self.pv_index if self.pivots[idx] == 1]
        valley_indices = [idx for idx in self.pv_index if self.pivots[idx] == -1]

        if peak_indices:
            sns.scatterplot(x=peak_indices, y=np.array(self.close_prices)[peak_indices],
                           color='yellow', marker='^', s=100, label='high')
        if valley_indices:
            sns.scatterplot(x=valley_indices, y=np.array(self.close_prices)[valley_indices],
                           color='blue', marker='v', s=100, label='low')

        # 3. 连接转折点
        sns.lineplot(x=self.pv_index, y=np.array(self.close_prices)[self.pv_index],
                    color='black', linestyle='--', alpha=0.7, linewidth=2, label='pivot line')

        # 4. 标记杯柄模式
        for pattern in self.cup_handle_results:
            points = pattern['points']
            x_coords = [points['A'][0], points['B'][0], points['C'][0], points['D'][0]]
            y_coords = [points['A'][1], points['B'][1], points['C'][1], points['D'][1]]
            sns.lineplot(x=x_coords, y=y_coords, color='red', linewidth=3, label='cup' if pattern == self.cup_handle_results[0] else "")

        plt.title('Kline')
        plt.xlabel('time')
        plt.ylabel('close_price')
        plt.legend()
        # plt.grid(True, alpha=0.3)
        # plt.tight_layout()
        plt.show()

    def get_plotting_instructions(self):
        """获取绘图指导说明"""
        if self.data is None or self.data.empty:
            return "请先调用 analyze_data() 方法分析数据"
        return "建议使用 plot_kline() 方法直接绘图"


def quick_analyze(data, plot=False):
    """快速分析函数 - 一键获取分析结果"""
    visualizer = KlineVisualizer()
    report = visualizer.analyze_data(data)

    if plot:
        visualizer.plot_kline()

    return {
        'report': report,
        'plotting_instructions': visualizer.get_plotting_instructions()
    }