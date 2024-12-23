import mesa
import random
from casevo import TotLog

# 代理：普通用户
class OrdinaryUserAgent(mesa.Agent):
    def __init__(self, unique_id, model, cur_person):
        super().__init__(unique_id, model)
        self.attitude = cur_person['original_atitude']  # 初始态度
        self.threshold = 0.1  # 设置一个阈值

    def step(self, core_neighbor):
        # 获取邻居代理
        for neighbor in core_neighbor:
            # 计算态度差异
            attitude_diff = abs(self.attitude - neighbor)
            # 如果态度差异在阈值内，则更新自己的态度
            if attitude_diff <= self.threshold:
                self.attitude = (self.attitude + neighbor) / 2
        # TotLog.add_agent_log(self.model.schedule.time, 'ordinary_attitude', self.attitude, self.unique_id)
        return self.attitude

# 代理：媒体用户
class MediaUserAgent(mesa.Agent):
    def __init__(self, unique_id, model, cur_person):
        super().__init__(unique_id, model)
        self.influence_score = cur_person['influence_score']
        self.attitude = 0.5  # 媒体用户态度保持中立

    # def step(self):
    #     # 获取邻居代理
    #     neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
    #     for neighbor in neighbors:
    #         if isinstance(neighbor, OrdinaryUserAgent):
    #             # 媒体用户影响普通用户的态度
    #             neighbor.attitude = (neighbor.attitude + self.attitude) / 2
