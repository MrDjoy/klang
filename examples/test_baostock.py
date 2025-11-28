import baostock as bs
lg = bs.login()
print('login respond error_code:' + lg.error_code)
print('login respond  error_msg:' + lg.error_msg)
kdata = bs.query_history_k_data_plus('sh.600276','date,open,high,low,close,volume', start_date='2022-04-20',frequency='d')
data = kdata.get_data()
print(data)