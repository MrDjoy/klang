import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt

# 获取贵州茅台的股票数据
maotai_data = yf.download("600519.SS", start="2020-01-01", end="2023-01-01")

# 选取收盘价数据
closing_prices = maotai_data['Close']

print(closing_prices.index)
# 使用 seaborn 绘制走势图
plt.figure(figsize=(12, 6))
sns.lineplot(x=closing_prices.index, y=closing_prices.values.ravel(), label='Maotai Closing Prices')
plt.title('Maotai Stock Closing Prices Over Time')
plt.xlabel('Date')
plt.ylabel('Closing Price (CNY)')
plt.legend()
plt.show()