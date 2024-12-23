from core_user_agent import CoreUserAgent
from ABM import MediaUserAgent, OrdinaryUserAgent

from casevo import ModelBase
from casevo import TotLog

import json
import pandas as pd

import random

class WeiboModel(ModelBase):
    def __init__(self, tar_graph, person_list, llm):
        """
        初始化微博模型。
        :param tar_graph: 目标图
        :param person_list: 总体用户列表
        :param llm: 语言模型
        """
        super().__init__(tar_graph, llm)
        with open('/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/content/background.txt', 'r', encoding='utf-8') as file:
            background = file.read()   
        self.background = background

        for cur_id in range(len(person_list)):
            cur_person = person_list[cur_id]
            if cur_id <= 735:
                cur_agent = CoreUserAgent(cur_id, self, cur_person, self.background)
                self.add_agent(cur_agent, cur_id)
            elif cur_id <= 1184:
                cur_agent = MediaUserAgent(cur_id, self, cur_person)
                self.add_agent(cur_agent, cur_id)
            else:
                cur_agent = OrdinaryUserAgent(cur_id, self, cur_person)
                self.add_agent(cur_agent, cur_id)
    def step(self):
        """
        执行模型的一步操作。
        """
        # 核心用户根据不同的激活概率随机激活
        activated_core_agents = []
        activated_core_user_ids = []
        activated_core_user_score = []

        for cur_agent in self.agents[:736]:  # 获取核心用户
            core_activation_probability = self.get_activation_probability(cur_agent)

            if random.random() < core_activation_probability:
                activated_core_agents.append(cur_agent)
                activated_core_user_ids.append(cur_agent.unique_id)
                activated_core_user_attitude_score = cur_agent.step()
                activated_core_user_score.append(activated_core_user_attitude_score)
        activated_core_user_num = len(activated_core_agents)

        # 2. 媒体用户接收核心用户激活数并更新自己的激活概率
        activated_media_agents = []
        activated_media_user_ids = []  # 记录激活的媒体用户ID
        for cur_agent in self.agents[736:1185]:
            media_activation_probability = self.get_activation_probability(cur_agent, 4) #activated_core_user_num
            if random.random() < media_activation_probability:
                activated_media_agents.append(cur_agent)
                activated_media_user_ids.append(cur_agent.unique_id) 
        activated_media_user_num = len(activated_media_agents)

        # 3. 普通用户根据核心用户的态度分数更新自己的态度分数
        activated_ordinary_agents = []
        activated_ordinary_user_ids = []
        activated_ordinary_user_score = []
        for cur_agent in self.agents[1185:]:
            ordinary_activation_probability = self.get_activation_probability(cur_agent, 4, activated_media_user_num) #activated_core_user_num
            if random.random() < ordinary_activation_probability:
                activated_ordinary_agents.append(cur_agent)
                activated_ordinary_user_ids.append(cur_agent.unique_id) 
                activated_ordinary_user_attitude_score = cur_agent.step(activated_core_user_score)
                activated_ordinary_user_score.append(activated_ordinary_user_attitude_score) 
        activated_ordinary_user_num = len(activated_ordinary_agents)

        round_info = {
            "round": self.schedule.time,
            "activated_core_user": activated_core_user_ids,  # 核心用户ID列表
            "activated_core_user_score":activated_core_user_score, #核心用户态度分数
            "activated_media_user": activated_media_user_ids,  # 媒体用户ID列表
            "activated_ordinary_user": activated_ordinary_user_ids,  # 普通用户ID列表
            "activated_ordinary_user_score": activated_ordinary_user_score, #普通用户态度分数
            "activated_core_user_num": activated_core_user_num,  # 核心用户数量
            "activated_media_user_num": activated_media_user_num,  # 媒体用户数量
            "activated_ordinary_user_num": activated_ordinary_user_num, # 普通用户数量
        }

        log_item = {
            'round_info': round_info
        }
        TotLog.add_model_log(self.schedule.time, 'round_info', log_item)
        print('round_info: %d end' % self.schedule.time)   
        self.schedule.time += 1  # 手动推进时间
            
    def get_activation_probability(self, agent, activated_core_user_num=None, activated_media_user_num=None):
        """
        根据代理类型获取激活概率。
        P(core) = P(core_base) 
            如果agent.influence_score > 100 P -= 0.01 if > 300 P -= 0.02
        P(media) = P(media_base) + α * N(core)（媒体用户激活概率依赖核心用户激活人数）
            如果agent.influence_score > 200 P -= 0.02 if > 400 P -= 0.04 
        P(user) = P(user_base) + β * N(media) + γ * N(core) * N(media)（普通用户激活概率依赖媒体用户和核心用户的互动）

        """
        if isinstance(agent, CoreUserAgent):
            base_probab = 0.1

            if agent.influence_score > 100:
                activation_probab = base_probab - 0.01
            elif agent.influence_score > 300:
                activation_probab = base_probab - 0.02
            else:
                activation_probab = base_probab
        elif isinstance(agent, MediaUserAgent):
            base_probab = 0.15
            a = 0.003
            activation_probab = base_probab + a * activated_core_user_num
            if agent.influence_score > 200:
                activation_probab -= 0.02
                if activation_probab > 1:
                    activation_probab = 1
            elif agent.influence_score > 400:
                activation_probab -= 0.04
                if activation_probab > 1:
                    activation_probab = 1
            else:
                pass
        else:
            base_probab =  0.2
            beta = 0.003
            gama = 0.00001
            activation_probab = base_probab + beta * activated_media_user_num + gama * activated_core_user_num * activated_media_user_num
            if activation_probab > 1:
                activation_probab = 1
        return activation_probab
        
