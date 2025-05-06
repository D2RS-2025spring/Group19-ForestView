#加载数据并进行初步检查
import pandas as pd
#数据类型为excel，名称为2018-2023北京气象补充.xlsx
df = pd.read_excel('2018-2023北京气象补充.xlsx') 
print(df.head())
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values(by='datetime')
df.set_index('datetime', inplace=True)
df.interpolate(method='time', inplace=True)
df['winddir'].fillna(df['winddir'].mode()[0], inplace=True)
#用箱线图快速检测异常值并剔除，参考北京极端气温-20摄氏度至40摄氏度,湿度不超过80%，降水不超过276.5mm，风速不超过30m/s
import seaborn as sns
import matplotlib.pyplot as plt
sns.boxplot(data=df['temp'])
plt.show()
df = df[(df['temp'] < 40) & (df['temp'] > -20)]
sns.boxplot(data=df['humidity'])
plt.show()
df = df[(df['humidity'] < 80) & (df['temp'] > -0)]
sns.boxplot(data=df['precip'])
plt.show()
df = df[df['precip'] < 276.5]
sns.boxplot(data=df['windspeed'])
plt.show()
df = df[(df['windspeed'] < 30) & (df['temp'] > -0)]
#选择特征工程
df['年'] = df.index.year
df['月'] = df.index.month
df['日'] = df.index.day
df['季度'] = df.index.quarter
#输出清洗后的数据
import os
os.makedirs('2018-2023数据清洗', exist_ok=True)  
df.to_csv('2018-2023数据清洗/cleaned_weather_2018_2023_data.csv')
#计算清洗后的数据月平均温度、湿度、降水、风速、海平面气压
df.index = pd.to_datetime(df.index)
#温度
monthly_avg_temp = df['temp'].resample('M').mean()
monthly_avg_temp = monthly_avg_temp.reset_index()
monthly_avg_temp.columns = ['months', 'avg temp']
monthly_avg_temp.to_csv('2018-2023数据清洗/monthly_avg_temp_2018-2023_data.csv', index=False)
#湿度
monthly_avg_temp = df['humidity'].resample('M').mean()
monthly_avg_temp = monthly_avg_temp.reset_index()
monthly_avg_temp.columns = ['months', 'avg humidity']
monthly_avg_temp.to_csv('2018-2023数据清洗/monthly_avg_humidity_2018-2023_data.csv', index=False)
#降水
monthly_avg_temp = df['precip'].resample('M').mean()
monthly_avg_temp = monthly_avg_temp.reset_index()
monthly_avg_temp.columns = ['months', 'avg precip']
monthly_avg_temp.to_csv('2018-2023数据清洗/monthly_avg_precip_2018-2023_data.csv', index=False)
#风速
monthly_avg_temp = df['windspeed'].resample('M').mean()
monthly_avg_temp = monthly_avg_temp.reset_index()
monthly_avg_temp.columns = ['months', 'avg windspeed']
monthly_avg_temp.to_csv('2018-2023数据清洗/monthly_avg_windspeed_2018-2023_data.csv', index=False)
#海平面气压
monthly_avg_temp = df['sealevelpressure'].resample('M').mean()
monthly_avg_temp = monthly_avg_temp.reset_index()
monthly_avg_temp.columns = ['months', 'avg sealevelpressur']
monthly_avg_temp.to_csv('2018-2023数据清洗/monthly_avg_sealevelpressure_2018-2023_data.csv', index=False)
