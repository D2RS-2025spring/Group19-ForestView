import pandas as pd
from pathlib import Path
import os

# —— 1. 路径配置 —— 
BASE_DIR  = Path(__file__).parent.parent    # 项目根目录
RAW_PATH  = BASE_DIR / 'data' / '2013-2018北京.csv'
DATA_DIR  = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# —— 2. 读取湿度数据 —— 
df = pd.read_csv(
    RAW_PATH,
    encoding='gbk',
    usecols=['datetime', 'humidity\n（湿度）']
)

# —— 3. 重命名、解析日期 —— 
df = df.rename(columns={
    'datetime': 'date',
    'humidity\n（湿度）': 'humidity'
})
df['date'] = pd.to_datetime(
    df['date'],
    format='%Y/%m/%d',
    errors='coerce'
)
df = df.dropna(subset=['date'])
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

# —— 4. 丢弃湿度缺失行 —— 
df = df.dropna(subset=['humidity'])

# —— 5. 以日期为索引并排序 —— 
df = df.set_index('date').sort_index()

# —— 6. 生成连续日序列并插值 —— 
df_daily_hum = (
    df['humidity']
    .resample('D')
    .mean()
    .interpolate('time')
)

# —— 7. 生成月平均（Month End） —— 
df_monthly_hum = df_daily_hum.resample('ME').mean()

# —— 8. 保存清洗结果 —— 
df_daily_hum.to_csv(DATA_DIR / 'clean_beijing_daily_humidity.csv',
                     header=['humidity'])
df_monthly_hum.to_csv(DATA_DIR / 'clean_beijing_monthly_humidity.csv',
                      header=['humidity'])

# —— 完成提示 —— 
print("湿度数据清洗完成：")
print(f"- 日数据：{df_daily_hum.index.min().date()} 至 {df_daily_hum.index.max().date()}，共 {len(df_daily_hum)} 条")
print(f"- 月数据：{df_monthly_hum.index.min().date()} 至 {df_monthly_hum.index.max().date()}，共 {len(df_monthly_hum)} 条")
