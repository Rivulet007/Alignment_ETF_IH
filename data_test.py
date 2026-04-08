import pandas as pd

# 1. 加载数据
df_etf = pd.read_csv('510050_SH_tick.csv')
df_fut = pd.read_csv('IH2512.csv')

# 2. 转换时间格式（为了提取日期）
# ETF: Unix 毫秒
df_etf['date_only'] = pd.to_datetime(df_etf['time'], unit='ms').dt.date
# 期货: Excel 序列值
df_fut['date_only'] = pd.to_datetime(df_fut['时间数'] - 25569, unit='D').dt.date

# 3. 统计日期分布
etf_dates = df_etf['date_only'].unique()
fut_dates = df_fut['date_only'].unique()

print("--- 数据存储格式检查 ---")

print(f"\n【ETF 数据】:")
print(f"包含交易日数量: {len(etf_dates)}")
print(f"具体日期: {etf_dates}")
if len(etf_dates) == 1:
    print("结论：这是【单日】存储格式。")
else:
    print("结论：这是【多日合一】存储格式。")

print(f"\n【期货 数据】:")
print(f"包含交易日数量: {len(fut_dates)}")
print(f"日期范围: {min(fut_dates)} 至 {max(fut_dates)}")
if len(fut_dates) == 1:
    print("结论：这是【单日】存储格式。")
else:
    print(f"结论：这是【多日合一】存储格式（共包含 {len(fut_dates)} 个交易日）。")