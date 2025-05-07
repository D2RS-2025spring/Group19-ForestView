#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# 1. 路径配置
BASE_DIR    = Path(__file__).resolve().parent.parent
RAW_CSV     = BASE_DIR / 'data' / '2013-2018北京.csv'
OUTPUT_DIR  = BASE_DIR / 'data'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 2. 读取并解析
df = pd.read_csv(
    RAW_CSV,
    encoding='gbk',
    usecols=[
        'datetime',
        'temp温度',
        'humidity\n（湿度）',
        'precip\n（降水）',
        'windspeed\n（风速）',
        'sealevelpressure\n（海平面气压）'
    ],
    parse_dates=['datetime']
)
df.rename(columns={
    'datetime': 'date',
    'temp温度': 'temperature',
    'humidity\n（湿度）': 'humidity',
    'precip\n（降水）': 'precip',
    'windspeed\n（风速）': 'windspeed',
    'sealevelpressure\n（海平面气压）': 'sealevelpressure'
}, inplace=True)
df.set_index('date', inplace=True)
for col in ['temperature', 'humidity', 'precip', 'windspeed', 'sealevelpressure']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. 日重采样 + 时间插值
daily = df.resample('D').mean().interpolate('time')

# 4. 月末重采样取平均
monthly = daily.resample('ME').mean()

# 5. 分别保存
metrics = {
    'temperature': 'monthly_avg_temperature.csv',
    'humidity': 'monthly_avg_humidity.csv',
    'precip': 'monthly_avg_precipitation.csv',
    'windspeed': 'monthly_avg_windspeed.csv',
    'sealevelpressure': 'monthly_avg_sealevelpressure.csv'
}

for col, fname in metrics.items():
    out_path = OUTPUT_DIR / fname
    monthly[[col]].to_csv(out_path, encoding='utf-8-sig')
    print(f"✅ 已保存 {col} 的月平均到：{out_path}")

