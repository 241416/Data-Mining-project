import pandas as pd
from casevo import AgentBase
from casevo import TotLog
from jinja2 import Template
import json
from utils import sentiment

# core agent
class CoreUserAgent(AgentBase):
    def __init__(self, unique_id, model, cur_person, background):
        self.tweets = pd.read_csv("/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/content/tweets.csv")
        description = f'用户id为{cur_person['user_id']},来自 {cur_person["ip"]},昵称为{cur_person['nickname']},人设是{cur_person['character']},在这件事的立场是{cur_person['view']}'
        context = f''

        super().__init__(unique_id, model, description, context)
        self.cur_person = cur_person
        self.background = background
        self.pos = None
        self.influence_score = cur_person['influence_score']

    def get_popular_tweets(self):  
        self.tweets = pd.read_csv("/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/content/tweets.csv")
     
        self.tweets['total_engagement'] = self.tweets['reposts_count'] + self.tweets['attitudes_count']
        popular_tweets = self.tweets[self.tweets['round'] == self.model.schedule.time - 1].nlargest(3, 'total_engagement')
        return popular_tweets[['id','user_id', 'text']].to_dict('records')

    def generate_weibo_action(self):
            if not self.tweets[(self.tweets['round'] == self.model.schedule.time - 1) & (self.tweets['user_id'] == self.cur_person['user_id'])].empty:
                self.context = f'{str(self.tweets[(self.tweets['round'] == self.model.schedule.time - 1) & (self.tweets['user_id'] == self.cur_person['user_id'])]['text'])}'
            # Step 1: 获取当前博主的背景信息以及立场
            input_data = {
                'description': self.description,
                'context': self.context,
                'background': self.background
            }
            # 读取第一个prompt模板文件，获取博主的立场
            prompt_file_path_1 = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/prompt/user_context.txt'
            with open(prompt_file_path_1, 'r', encoding='utf-8') as file:
                prompt_template_1 = file.read()

            # 渲染第一个prompt模板
            template_1 = Template(prompt_template_1)
            rendered_prompt_1 = template_1.render(
                description=input_data['description'],
                context=input_data['context'],
                background=input_data['background']
            )            
            response_1 = self.model.llm.send_message(rendered_prompt_1)
    
            # Step 2: 分析热门微博内容        
            prompt_file_path_2 = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/prompt/analysis_steps.txt'  # 模板2路径
            with open(prompt_file_path_2, 'r', encoding='utf-8') as file:
                prompt_template_2 = file.read()

            popular_tweets_list = self.get_popular_tweets()
            input_data['popular_tweets_list'] = popular_tweets_list
            template_2 = Template(prompt_template_2)
            rendered_prompt_2 = template_2.render(
                description=input_data['description'],
                viewpoint = response_1,
                popular_tweets_list=input_data['popular_tweets_list']
            )

            response_2 = self.model.llm.send_message(rendered_prompt_2)
            print(response_2)
            response_json_2 = json.loads(response_2)
            action_type = response_json_2.get('action_type')
            weibo_id = response_json_2.get('id')
            user_id = response_json_2.get('user_id')
            text = response_json_2.get('text')
            attitude_score = sentiment(text)

            # 执行最终操作
            if action_type == '发微博':
                new_tweet = {
                    'round': self.model.schedule.time,
                    'id': weibo_id,
                    'user_id': user_id,
                    'text': text,
                    'attitudes_count': 0,
                    'reposts_count': 0
                }
                new_tweet_df = pd.DataFrame([new_tweet])
                new_tweet_df = new_tweet_df.fillna(0)

                self.tweets = pd.concat([self.tweets, new_tweet_df], ignore_index=True)

            elif action_type == '转发':
                self.tweets.loc[self.tweets['id'] == weibo_id, 'reposts_count'] += 1
                print("")
            elif action_type == '点赞':
                self.tweets.loc[self.tweets['id'] == weibo_id, 'attitudes_count'] += 1
            else:
                pass 
            output_path = '/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/content/tweets.csv'
            self.tweets.to_csv(output_path, encoding='utf-8')

            return {
                'action_type': action_type,
                'user_id': user_id,
                'id': weibo_id,
                'text': text,
                'attitude_score': attitude_score
            }
        
    def step(self):
        tmp_result = self.generate_weibo_action()
            
        # 记录日志
        log_item = {
            'action': tmp_result
        }
        TotLog.add_agent_log(self.model.schedule.time, 'core_user_action', log_item, self.unique_id)
        return tmp_result['attitude_score']