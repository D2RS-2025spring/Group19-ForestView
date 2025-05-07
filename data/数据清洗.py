import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# —— 1. 路径设置 —— 
BASE_DIR   = Path(__file__).parent.parent    # 项目根目录
DATA_DIR   = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

RAW_CSV    = DATA_DIR / '2013-2018北京.csv'
CLEAN_CSV  = DATA_DIR / 'cleaned_weather_data.csv'
BOXPLOT_PNG = OUTPUT_DIR / 'boxplots_outliers.png'

# —— 2. 读取原始数据 —— 
df = pd.read_csv(
    RAW_CSV,
    encoding='gbk',
    usecols=[
        'datetime',
        'temp温度',
        'humidity\n（湿度）',
        'precip\n（降水）',
        'windspeed\n（风速）',
        'sealevelpressure\n（海平面气压）',
        'preciptype\n（降水类型）',
        'conditions\n（气象条件）'
    ],
    parse_dates=['datetime']
)

# —— 3. 重命名列 —— 
df = df.rename(columns={
    'datetime': 'date',
    'temp温度': 'temperature',
    'humidity\n（湿度）': 'humidity',
    'precip\n（降水）': 'precip',
    'windspeed\n（风速）': 'windspeed',
    'sealevelpressure\n（海平面气压）': 'sealevelpressure',
    'preciptype\n（降水类型）': 'precip_type',
    'conditions\n（气象条件）': 'conditions'
})

# —— 4. 设置索引并排序 —— 
df = df.set_index('date').sort_index()

# —— 5. 连续型数据转数值 & 初步缺失填充 —— 
cont_cols = ['temperature', 'humidity', 'precip', 'windspeed', 'sealevelpressure']
df[cont_cols] = df[cont_cols].apply(pd.to_numeric, errors='coerce')

# 时间序列插值，补全缺失
df[cont_cols] = (
    df[cont_cols]
    .interpolate(method='time')
    .fillna(method='ffill')
    .fillna(method='bfill')
)

# —— 6. 分类数据缺失填充 —— 
cat_cols = ['precip_type', 'conditions']
for c in cat_cols:
    mode = df[c].mode().iloc[0] if not df[c].mode().empty else 'unknown'
    df[c] = df[c].fillna(mode).replace('', 'unknown')

# —— 7. 特征工程 —— 
df['year']    = df.index.year
df['month']   = df.index.month
df['quarter'] = df.index.quarter

# —— 8. 异常值检测：绘制箱线图 —— 
plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
df['temperature'].plot.box()
plt.title('Temperature')

plt.subplot(1,2,2)
df['precip'].plot.box()
plt.title('Precipitation')

plt.tight_layout()
boxplot_path = OUTPUT_DIR / 'boxplots_outliers.png'
plt.savefig(boxplot_path, dpi=300, bbox_inches='tight')
print(f"✅ 箱型图已保存到：{boxplot_path}")
plt.show()

# —— 9. 标记并删除异常值 —— 
# 温度域外阈值
temp_mask = (df['temperature'] < -30) | (df['temperature'] > 50)
print(f"检测到温度异常 {temp_mask.sum()} 条，已标记为 NaN")
df.loc[temp_mask, 'temperature'] = np.nan

# 降水 IQR 方法
Q1 = df['precip'].quantile(0.25)
Q3 = df['precip'].quantile(0.75)
IQR = Q3 - Q1
precip_mask = (df['precip'] < Q1 - 1.5 * IQR) | (df['precip'] > Q3 + 1.5 * IQR)
print(f"检测到降水异常 {precip_mask.sum()} 条，已标记为 NaN")
df.loc[precip_mask, 'precip'] = np.nan

# —— 10. 异常值插值填充 —— 
df['temperature'] = (
    df['temperature']
    .interpolate(method='time')
    .fillna(method='ffill')
    .fillna(method='bfill')
)
df['precip'] = (
    df['precip']
    .interpolate(method='time')
    .fillna(0)
)

# —— 11. 保存最终清洗后的数据 —— 
df.to_csv(CLEAN_CSV, encoding='utf-8-sig')
print(f"清洗完成，输出文件：{CLEAN_CSV}")
