import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import json

# 生成图
node_num = 4888
graph = nx.complete_graph(node_num)
graph_data = json_graph.node_link_data(graph)

# 加载节点的配置数据
with open('dataset/core.json') as f:
    core_data = json.load(f)
    
with open('dataset/media.json') as f:
    media_data = json.load(f)
    
with open('dataset/ordinary.json') as f:
    ordinary_data = json.load(f)

user_list = core_data + media_data + ordinary_data

# 配置输出
output_item = {
    "graph": graph_data,
    "person": user_list 
}

# 输出实验配置文件
with open('case_lite.json', 'w') as f:
    json.dump(output_item, f, ensure_ascii=False)

