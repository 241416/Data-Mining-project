'''
format: the probability density map 
    core_user: influence_score original_atitude,
    media_user: influence_score,
    ordinary_user: original_atitude
'''

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 读取 JSON 文件
core_path = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/dataset/core.json' 
core = pd.read_json(core_path)
media_path = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/dataset/media.json' 
media = pd.read_json(media_path)
ordinary_path = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/dataset/ordinary.json' 
ordinary = pd.read_json(ordinary_path)

core_influence = core['influence_score']
core_origi_attitude = core['original_atitude']
media_influence = media['influence_score']
ordinary_attitude = ordinary['original_atitude']

# 设置画布大小
plt.figure(figsize=(10, 6))

# 绘制概率密度曲线
sns.kdeplot(data=ordinary_attitude, label='Original Attitude', fill=True, color='blue', alpha=0.6)

# 添加图例
plt.legend(title="Legend")

# 设置标题和标签
plt.title('Probability Density Curve of Original Attitude of Ordinary Users')
plt.xlabel('Original Attitude')
plt.ylabel('Density')

# 保存图片
plt.savefig('ordinary_original_attitude.png')

# 显示图形
plt.show()