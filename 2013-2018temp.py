import pandas as pd # type: ignore
import os
from pathlib import Path

# —— 确保 data/ 和 output/ 目录存在 —— 
BASE_DIR = Path(__file__).parent      # src/ 所在目录
DATA_DIR = (BASE_DIR / '..' / 'data').resolve()
OUTPUT_DIR = (BASE_DIR / '..' / 'output').resolve()

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    'D:/13192/D2RS-v20250306/vicky/2013-2018北京.csv',
    encoding='gbk',               # 文件编码
    usecols=['datetime', 'temp温度']  # 只保留日期和平均温度两列
)
# 2. 重命名列
df.columns = ['date', 'temperature']
# 3. 解析日期
df['date'] = pd.to_datetime(
    df['date'],
    format='%Y/%m/%d',            # 与 CSV 中的日期格式对应
    errors='coerce'               # 解析失败会变成 NaT
)

# 4. 丢弃解析失败或温度缺失的行
df = df.dropna(subset=['date', 'temperature'])

# 5. 确保温度为数值类型
df['temperature'] = pd.to_numeric(
    df['temperature'],
    errors='coerce'
)
df = df.dropna(subset=['temperature'])

# 6. 以日期为索引并排序
df = df.set_index('date').sort_index()

# 7. 生成连续的每日序列并插值填补空缺
df_daily = (
    df['temperature']
    .resample('D')       # 按天重采样
    .mean()              # 对已有数据取平均
    .interpolate('time') # 时间线性插值
)

# 8. （可选）生成月平均序列
df_monthly = df_daily.resample('ME').mean()


# 9. 保存清洗后数据
# 保存清洗后数据
df_daily.to_csv(DATA_DIR / 'clean_beijing_daily.csv', header=['temperature'])
df_monthly.to_csv(DATA_DIR / 'clean_beijing_monthly.csv', header=['temperature'])

