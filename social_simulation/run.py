import os
from networkx.readwrite import json_graph
import networkx as nx
import json
import matplotlib.pyplot as plt
from model import WeiboModel
import argparse
from baichuan import BaichuanLLM
import pandas as pd

from casevo import TotLog

API_KEY = 'sk-049083994ddb576e074207329674b28a'

parser = argparse.ArgumentParser(description='Run the Mesa model.')

# 添加配置文件作为参数
parser.add_argument('filename', metavar='config_file', type=str,
                   help='The config file for the sim')
parser.add_argument('round', metavar='round_num', type=int,
                   help='The round number of the sim')

args = parser.parse_args()

tar_file = args.filename

with open(tar_file, 'r') as f:
    config_file = json.load(f)

# 获取配置
G = json_graph.node_link_graph(config_file['graph'])
# print("G is", G)

person_list = config_file['person']

# 绘制社交图（可选）
# nx.draw(G, with_labels=True)
# plt.savefig('graph.png')

log_path = './log/'
memory_path = './memory/'

# 创建日志和内存路径
if not os.path.exists(log_path):
    os.makedirs(log_path)
if not os.path.exists(memory_path):
    os.makedirs(memory_path)

# 初始化日志
TotLog.init_log(4888, if_event=True)

# 初始化LLM
llm = BaichuanLLM(API_KEY, 3)

# 引入模型
model = WeiboModel(G, person_list, llm) 

# 运行模拟
try:
    for i in range(args.round):
        model.step()
except Exception as e:
    print(f"Error during model step: {e}")

# 输出日志
TotLog.write_log(log_path)