import networkx as nx
import random
import os
import math
import json
with open(r'C:\Users\86152\Documents\WeChat Files\wxid_1p912q9vszgs22\FileStorage\File\2024-12\event(2).json','r',encoding='utf-8') as file:
    data = json.load(file)
core_number_list=[]
for i in data:
    if i['owner'] =='model':
        # core_number = i['item']['round_info']['activated_core_user_num']
        core_number = data.index(i)
        core_number_list.append(core_number)
print(core_number_list)
#[69, 63, 81, 73, 69, 76, 82, 66, 75, 71]
core_number_list=[69, 133, 215, 289, 359, 436, 519, 586, 662, 734] ##这里记录了每一轮中的日志情况
for m in range(len(core_number_list)):
    print(m)
    ts0=data[core_number_list[m]]['item']['round_info']
    #首先来看ts=0时大家发言与得分
    G = nx.DiGraph()

    # 添加节点
    for i in range(1, 4887):
        if i < 732:
            if i in ts0['activated_core_user']:
                if m==0:
                    index_1 = ts0['activated_core_user'].index(i)
                    index_2 = ts0['activated_core_user'].index(i)
                else:
                    index_1 = ts0['activated_core_user'].index(i)
                    index_2 = ts0['activated_core_user'].index(i)+core_number_list[m-1]+1
                # print(index_)
                index_content = data[index_2]["item"]["action"]["text"]
                action_type = data[index_2]["item"]["action"]["action_type"]
                G.add_node(i, label="core-"+str(i), content=action_type+":"+index_content,color='#ff5575', size=11,score=ts0['activated_core_user_score'][index_1],group = 1)
        elif i >= 733 and i < 1185:
            if i in ts0['activated_media_user']:
                G.add_node(i, label="media-"+str(i),content='保持中立', color='#ffd36a', size=10,score=0.5,group = 2)
        else:
            if i in ts0['activated_ordinary_user']:
                index_2 = ts0['activated_ordinary_user'].index(i)
                G.add_node(i, label="ordinary-"+str(i), content="情感得分:"+str(ts0['activated_ordinary_user_score'][index_2]), color='#6299ff', size=6,score=ts0['activated_ordinary_user_score'][index_2],group = 3)


    # pos = nx.spring_layout(G, seed=1234)  # 设置随机种子以确保位置一致性
    # # 添加节点的 x 和 y 坐标到每个节点
    # for node, coords in pos.items():
    #     G.nodes[node]['x'] = coords[0]
    #     G.nodes[node]['y'] = coords[1]


    pos = nx.spring_layout(G, seed=1234)

    # 为每个组设置不同的半径
    group_radii = {
        1: 1.0,  # group1在最小半径的圈内部分
        2: 2.0,  # group2在稍大的圈内部分
        3: 3.0   # group3在更大的圆环范围内
    }

    # 根据组分配不同的坐标
    for node in G.nodes():
        group = G.nodes[node]['group']
        radius = group_radii[group]
        theta = random.uniform(0, 2 * 3.14159)  # 随机角度
        G.nodes[node]['x'] = random.uniform(radius * math.cos(theta),radius * math.cos(theta)+2)
        G.nodes[node]['y'] = random.uniform(radius * math.sin(theta),radius * math.sin(theta)+2)



    def should_connect(node1, node2):
        m1 = G.nodes[node1]['score']
        m2 = G.nodes[node2]['score']
        n1 = G.nodes[node1]['group']
        n2 = G.nodes[node2]['group']
        score_difference = abs(m1 - m2)
        if score_difference <=0.01 and n1!=n2:
            return True
        return False

    for i in G.nodes():
        for j in G.nodes():
            if i != j and should_connect(i, j):
                # 这里可以添加边的属性，例如权重等
                G.add_edge(i, j,color ='#DCDCDC',alpha=0.3)

    # 使用 nx.write_gexf 保存 GEXF 文件
    base_path = './my_vue/public'
    filename = f"arctic_{m}.gexf"
    
    # 完整的文件路径
    full_path = os.path.join(base_path, filename)
    nx.write_gexf(G, full_path)








