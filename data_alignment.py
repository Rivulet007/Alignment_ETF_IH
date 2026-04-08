"""
进行2025年10月31号单日的处理，调整etf时间戳为北京时间，以期货为基准找最新etf价格，进行对齐
输出四个主力合约的数据（包括时间、期货和现货买卖价格、基差）和对齐质量报告
"""

import pandas as pd
import os

# 1. 定义合约列表和配置
contracts = ['IH2511', 'IH2512', 'IH2603', 'IH2606']
target_date = '2025-10-31'

# 2. 预处理 ETF 数据
df_etf = pd.read_csv('510050_SH_tick.csv')
# 修复时区
df_etf['datetime'] = pd.to_datetime(df_etf['time'], unit='ms') + pd.Timedelta(hours=8)
# 提取日期
df_etf_day = df_etf[df_etf['datetime'].dt.strftime('%Y-%m-%d') == target_date].copy()
df_etf_day = df_etf_day.sort_values('datetime')

# 处理 ETF 增量成交量
# 使用 diff() 计算当前行与上一行的差值 (n1 - n0)
df_etf_day['volume_delta'] = df_etf_day['volume'].diff().fillna(0)

# 检验
if df_etf_day.empty:
    print(f" 【错误❌】：ETF 数据中未找到 {target_date}")
else:
    print(f" 【正确☑️】：ETF 数据就绪，当日样本量: {len(df_etf_day)}")

# 3. 循环处理每个期货合约
for contract in contracts:
    file_name = f'{contract}.csv'

    if not os.path.exists(file_name):
        print(f" 【跳过❌】：文件 {file_name} 不存在")
        continue

    print(f"\n--- 正在处理合约: {contract} ---")

    # 加载期货数据
    df_fut = pd.read_csv(file_name)

    # 转换期货时间
    df_fut['datetime'] = pd.to_datetime(df_fut['时间数'] - 25569, unit='D')

    # 提取目标日期
    df_fut_day = df_fut[df_fut['datetime'].dt.strftime('%Y-%m-%d') == target_date].copy()
    df_fut_day = df_fut_day.sort_values('datetime')

    if df_fut_day.empty:
        print(f" 【错误❌】 该合约在 {target_date} 没有交易数据")
        continue

    # 4. 执行对齐逻辑 (merge_asof)
    # 这里的列表加入了新增的 'volume_delta'
    df_aligned = pd.merge_asof(
        df_fut_day,
        df_etf_day[['datetime', 'lastPrice', 'askPrice', 'bidPrice']],
        on='datetime',
        direction='backward'
    )

    # 5. 计算Basis
    df_aligned['basis'] = df_aligned['最新'] - df_aligned['lastPrice'] * 1000

    # 6. 输出
    # 加入期货的买一和卖一价格，以及 ETF 的增量成交量
    output_columns = [
        'datetime',
        '最新', '卖一价', '买一价',  # 期货端价格
        'lastPrice', 'askPrice', 'bidPrice', # ETF端价格
        'basis'
    ]

    df_final = df_aligned[output_columns].dropna()

    # 重命名列名
    # 时间，期货最新价，期货卖一价，期货买一价，etf最新价，etf卖一价，etf买一价，基差
    df_final.columns = ['datetime', 'fut_last', 'fut_ask', 'fut_bid', 'etf_last', 'etf_ask', 'etf_bid', 'basis']

    output_file = f'aligned_{contract}_{target_date}.csv'
    df_final.to_csv(output_file, index=False, encoding='utf_8_sig')

    # 合约质量报告
    print(f" 对齐成功: {len(df_final)} 行")
    print(f" 基差统计: 均值 {df_final['basis'].mean():.2f}, 标准差 {df_final['basis'].std():.2f}")
    print(f" 已保存至: {output_file}")

print("\n 所有合约处理完毕。")