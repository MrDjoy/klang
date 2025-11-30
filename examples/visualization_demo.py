"""
可视化模块使用示例 - 集成转折点检测和杯柄模式识别
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Klang import Klang
from Klang.pattern.visualization import KlineVisualizer, quick_analyze

def main():
    """主函数 - 展示完整的可视化分析流程"""
    try:
        # 1. 初始化Klang并获取数据
        print("步骤1: 初始化Klang并加载股票数据...")
        Klang.Klang_init()
        kl = Klang.Kl

        # 设置股票代码和时间范围
        stock_code = 'sh.600004'
        kl.date(start='2024-05-01', end='2025-11-28')
        kl.code(stock_code)
        # 获取K线数据
        data = kl.day_df
        if data is None:
            print(f"× 加载股票 {stock_code} 数据失败，请检查数据源或网络连接")
            return
        print(f"✓ 成功加载股票 {stock_code} 数据，共 {len(data)} 个交易日")

        # 2. 使用可视化分析器
        print("步骤2: 分析数据并检测模式...")
        visualizer = KlineVisualizer()
        analysis_result = visualizer.analyze_data(data)

        # 3. 显示分析结果
        print("\n" + "="*50)
        print("分析结果摘要:")
        print("="*50)

        report = analysis_result
        summary = report['summary']
        print(f"数据点数量: {summary['data_points']}")
        print(f"转折点数量: {summary['pivot_points']}")
        print(f"检测到的杯柄模式: {summary['cup_handle_patterns']}")

        # 显示转折点详情
        print(f"\n转折点详情 (前5个):")
        for i, pivot in enumerate(report['pivots'][:5]):
            print(f"  {i+1}. 位置: {pivot['index']}, 类型: {pivot['type']}, 价格: {pivot['price']:.2f}")

        # 显示杯柄模式详情
        if report['patterns']:
            print(f"\n杯柄模式详情:")
            for i, pattern in enumerate(report['patterns']):
                points = pattern['points']
                print(f"  模式 {i+1}:")
                for label, (idx, price) in points.items():
                    print(f"    {label}点: 位置 {idx}, 价格 {price:.2f}")

        # 4. 获取绘图指导
        print("\n" + "="*50)
        print("绘图使用说明:")
        print("="*50)

        visualizer.plot_kline()
        # print(plotting_guide)

        # 5. 快速分析示例（一键式）
        print("\n" + "="*50)
        print("快速分析示例:")
        print("="*50)

        quick_result = quick_analyze(data)
        print("✓ 快速分析完成")

        # 保存绘图代码到文件（可选）
        with open('plotting_guide.py', 'w') as f:
            f.write(plotting_guide)
        print("✓ 绘图指导已保存到 plotting_guide.py")

        print("\n🎯 下一步操作:")
        print("1. 安装matplotlib: pip install matplotlib")
        print("2. 查看 plotting_guide.py 文件中的绘图代码")
        print("3. 运行绘图代码: python plotting_guide.py")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保项目已正确安装：python setup.py install")
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()