import pandas as pd
import os
from pathlib import Path

# —— 1. 准备路径 —— 
BASE_DIR    = Path(__file__).parent
DATA_DIR    = (BASE_DIR / '..' / 'data').resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH    = DATA_DIR / '2013-2018北京.csv'

# —— 2. 读取原始数据，只保留 降水量 和 降水类型 列 —— 
df = pd.read_csv(
    RAW_PATH,
    encoding='gbk',
    usecols=[
        'datetime',
        'precip\n（降水）',
        'preciptype\n（降水类型）'
    ]
)

# —— 3. 重命名列 —— 
df = df.rename(columns={
    'datetime': 'date',
    'precip\n（降水）': 'precip',
    'preciptype\n（降水类型）': 'precip_type'
})

# —— 4. 解析日期并丢弃无效行 —— 
df['date'] = pd.to_datetime(
    df['date'],
    format='%Y/%m/%d',
    errors='coerce'
)
df = df.dropna(subset=['date'])

# —— 5. 清洗降水量 —— 
# 转为数值，非数字或缺失填 0（表示无降水）
df['precip'] = pd.to_numeric(df['precip'], errors='coerce').fillna(0)

# —— 6. 清洗降水类型 —— 
# 缺失时标记为 'none'，去除前后空格并统一小写
df['precip_type'] = (
    df['precip_type']
    .fillna('none')
    .astype(str)
    .str.strip()
    .str.lower()
    .replace({'': 'none'})
)

# —— 7. 设置索引并排序 —— 
df = df.set_index('date').sort_index()

# —— 8. （可选）生成连续日序列 —— 
#    如果想要后续分析方便，可把每日降水和降水类型补全到每日
df_daily_precip = (
    df['precip']
    .resample('D')
    .sum()                   # 每日总降水
)
df_daily_type = (
    df['precip_type']
    .resample('D')
    .agg(lambda x: x.mode()[0] if not x.mode().empty else 'none')
)

# —— 9. 保存清洗结果 —— 
df_daily_precip.to_csv(DATA_DIR / 'clean_beijing_daily_precip.csv',
                       header=['precip'])
df_daily_type.to_csv(DATA_DIR / 'clean_beijing_daily_precip_type.csv',
                     header=['precip_type'])
