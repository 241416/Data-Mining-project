import pandas as pd
import json
from sklearn.preprocessing import RobustScaler
import os
import openai
import yaml

# 读取YAML配置文件
def read_config(config_file_path):
    with open(config_file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def influencer_profile_summarize(influencer_dirpath, api_key):
    '''
    功能：遍历influencer_profile所在目录中的每一个文件夹，找到json文件，综合用户介绍和最近发过的5条微博，得到这个大V的描述，用于LLM模拟
    方法：gpt3.5-turbo auto-summarize
    输入：
        influencer_dirpath(str)
    输出：
        dict
        {'name1':'description',
        'name2':'description'
        }
    '''
    # GPT-3.5 API密钥配置
    openai.api_key = api_key
    openai.base_url = "https://free.v36.cm/v1/"
    openai.default_headers = {"x-foo": "true"}

    influencer_profiles = {}

    # 遍历目录
    for folder_name in os.listdir(influencer_dirpath):
        folder_path = os.path.join(influencer_dirpath, folder_name)

        # 只处理文件夹
        if os.path.isdir(folder_path):
            json_file_path = os.path.join(folder_path, f'{folder_name}.json')
            
            # 检查是否存在json文件
            if os.path.exists(json_file_path):
                # 读取json文件
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取用户的名字（假设json文件包含'username'字段）
                name = folder_name
                
                # 提取用户介绍（假设json文件包含'introduction'字段）
                introduction = data.get('user', 'No introduction available.')
                
                # 提取最近5条微博（假设json文件包含'tweets'字段）
                recent_tweets = data.get('weibo', [])
                recent_tweets_text = " ".join([tweet.get('text', '') for tweet in recent_tweets[:5]])

                # 合并用户介绍和最近微博内容
                user_content = f"简介: {introduction} 最近的微博内容: {recent_tweets_text}"
                prompt=f"根据以下信息为该用户总结一个流畅的简洁介绍，用于LLM模拟该微博用户,不多于200个字：{user_content}"
                completion = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
                influencer_profiles[name] = completion.choices[0].message.content
    return influencer_profiles


def personality_labeling(text,api_key):

    '''
    用gpt-3.5对每一条微博文本进行打标签

    input:
        text(string)
    return:
        [character(string), viewpoint]
   '''

    openai.api_key = api_key
    openai.base_url = "https://free.v36.cm/v1/"
    openai.default_headers = {"x-foo": "true"}

    prompt = f"""
    请根据给定的文本，判断并输出该段话所属的类型和人设。你可以对人设进行适当修改，但类型必须严格属于以下8种之一：

    类型：
    自我牺牲型母亲：常常把自己放在家庭中的最后，认为自己不重要，乐意为家人牺牲。她可能会想，“孩子们最需要，我得为他们着想。”
    传统性别分工型丈夫：表现出一种传统性别角色分配的态度，认为自己应优先享受资源，妻子和孩子次之。
    情感需求型妻子：通过“瑞士卷怎么分”来测试丈夫的关心与爱，期待丈夫能在细节上关注自己。
    反感性别对立观点：批判这种讨论，认为现代人应该理性看待家庭关系，而非将所有争议聚焦在琐事上。
    现代家庭独立型女性：自信、独立，认为婚姻中的平等与自我照顾同样重要，推崇个人的自由选择。
    幽默反转型男性：风趣、调侃，以轻松幽默的方式处理日常生活中的小冲突。
    消费降级批判型：认为这种讨论是无意义的消费文化的体现，对这种过度关心“吃”以及“分配”方式感到厌倦。
    借势营销商家：利用事件热度，紧跟热点话题，增加曝光度，通过与用户情感共鸣的内容传递产品信息，提升品牌亲和力。

    格式要求：
    返回类型，例如
    类型

    以下是给定文本：
    "{text}"
    """
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def sentiment_gpt(text, api_key):
      '''
    用gpt-3.5对每一条微博文本进行情感得分打分
    0-1 非常负面到非常正面

    input:
        text(string)
    return:
        float
   '''      
      openai.api_key = api_key
      openai.base_url = "https://free.v36.cm/v1/"
      openai.default_headers = {"x-foo": "true"}
      prompt = f"""
    请根据给定的文本，判断这段话的情感得分（从0到1，非常负面到非常正面）
    仅需要返回情感得分（float），
    返回格式举例：0.3

    以下是给定文本：
    "{text}"
    """
      completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
            ],
            )
      return completion.choices[0].message.content


def divide_users(ori_data_path, start_time, contribution_dict,character_description_dict,previous_tweets_path, api_key, influencer_profile_dict):
    df = pd.read_csv(ori_data_path)
    df = df.dropna(subset=['user_authentication'])

    core_data = []
    ordinary_data = []
    media_data = []

    tweets_data = []

    # 计算核心用户和媒体用户的影响力分数
    df['total_interactions'] = df['attitudes_count'] + df['comments_count'] + df['reposts_count']

    max_core_influence = df[df['user_authentication'].isin(['金V', '红V'])]['total_interactions']
    max_media_influence = df[df['user_authentication'] == '蓝V']['total_interactions']

    # 创建鲁棒缩放器并进行拟合
    scaler = RobustScaler()
    scaler.fit(max_core_influence.values.reshape(-1, 1))  # 对核心用户数据拟合
    scaler.fit(max_media_influence.values.reshape(-1, 1))  # 对媒体数据拟合

    for _, row in df.iterrows():
        user_info = {
            'user_id': row['user_id'],
            'nickname': row['screen_name']
            }

        previous_tweets = {
            'round': -1,
            'weibo_id': row['id'],
            'id': row['user_id'],
            'text': row['text'],
            'attitudes_count': row['attitudes_count'],
            'reposts_count': row['reposts_count'],
            'attitude_score': sentiment(row['text'])
        }
       
        # core user
        if row['user_authentication'] in ['金V', '红V'] or contribution_dict.get(row['screen_name']) is not None:
            user_info['character'] = personality_labeling(row['text'], api_key)
            user_info['view'] = character_description_dict.get(user_info['character'])
            if influencer_profile_dict.get(user_info['nickname']) is not None:
                user_info['view'] += influencer_profile_dict.get(user_info['nickname'])
            user_info['ip'] = row['ip'] if pd.notna(row['ip']) else '未知'
            influence_score = row["attitudes_count"] + row["comments_count"] + row["reposts_count"]
            # 使用鲁棒缩放器进行归一化
            user_info['influence_score'] = scaler.transform([[influence_score]])[0][0]
            tweet_date = row['created_at']
            if tweet_date <= start_time:
                user_info['original_atitude'] = previous_tweets['attitude_score']
                user_info['original_text'] = previous_tweets['text']
                tweets_data.append(previous_tweets)
            else:
                user_info['original_atitude'] = 0.5
                user_info['original_text'] = None
            core_data.append(user_info)

        # media
        elif row['user_authentication'] == '蓝V': 
            influence_score = row["attitudes_count"] + row["comments_count"] + row["reposts_count"]
            # 使用鲁棒缩放器进行归一化
            user_info['influence_score'] = scaler.transform([[influence_score]])[0][0]
            user_info['original_atitude'] = 0.5
            media_data.append(user_info)

        # ordinary user
        else:
            tweet_date = row['created_at']
            if tweet_date <= start_time:
                user_info['original_atitude'] = sentiment(previous_tweets['text'])
            else:
                user_info['original_atitude'] = 0.5
            ordinary_data.append(user_info)

    previous_tweets_df = pd.DataFrame(tweets_data)
    previous_tweets_df.to_csv(previous_tweets_path, index=False)

    return save_tojson(core_data,'core.json'), save_tojson(ordinary_data,'ordinary.json'), save_tojson(media_data,'media.json')


def update_core_json_with_influencer_profile(core_json_path, influencer_profile_dict, output_json_path):
    with open(core_json_path, 'r', encoding='utf-8') as f:
        core_data = json.load(f)

    for item in core_data:
        nickname = item.get('nickname')
        
        # 如果nickname存在于influencer_profile_dict中，更新'view'字段
        if nickname in influencer_profile_dict:
            # 获取该用户的描述信息
            influencer_description = influencer_profile_dict[nickname]
            item['view'] += f" {influencer_description}"

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(core_data, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    # openai_api_url = 'https://free.v36.cm'

    # 读取配置文件
    config = read_config('/Users/taijieshengwu/Documents/专业课（大三下）/ZJX/SRE/config.yaml')

    # 通过配置文件获取参数
    contribution_excel_path = config['contribution_excel_path']
    contribution_csv_path = config['contribution_csv_path']
    previous_tweets_path = config['previous_tweets_path']
    ori_data_path = config['ori_data_path']
    start_time = config['start_time']
    openai_key = config['openai_key']
    character_description_dict = config['character_description_dict']   
    influencer_dirpath = config['influencer_dirpath']
    core_json_path = config['core_json_path'] 
    ordinary_json_path = config['ordinary_json_path']

    contribution_df = pd.read_csv(contribution_csv_path)
    contribution_dict = contribution_df.set_index('screen_name')['contribution_score'].to_dict()
    
    influencer_profile_dict = influencer_profile_summarize(influencer_dirpath, openai_key)
    divide_users(ori_data_path, start_time, contribution_dict,character_description_dict,previous_tweets_path,openai_key, influencer_profile_dict)
    update_core_json_with_influencer_profile(core_json_path, influencer_profile_dict, core_json_path)
    

    # 因为前面的有的没达到效果，额外对core.json和ordinary.json做了一些修改
    # with open(ordinary_json_path, 'r', encoding='utf-8') as f:
    #     ordinary_data = json.load(f)

    # df = pd.read_csv(ori_data_path)
    # df = df.dropna(subset=['user_authentication'])

    # for item in ordinary_data:
    #     nickname = item.get('nickname')
    #     text = ', '.join(df[df['screen_name']==nickname]['text'].astype(str))
    #     item['original_atitude'] = sentiment(text)
    
    # with open(ordinary_json_path, 'w', encoding='utf-8') as f:
    #     json.dump(ordinary_data, f, ensure_ascii=False, indent=4)

    # df_sorted = df.sort_values(by='created_at') 

    # # 2. 创建一个空的 DataFrame 用于存储符合条件的 tweet
    # tweets = pd.DataFrame(columns=['round','id', 'user_id', 'screen_name', 'text', 'attitudes_count', 'comments_count', 'reposts_count'])

    # # 3. 遍历 df_sorted，筛选并添加符合条件的行
    # for _, row in df_sorted.iterrows():
    #     if row['user_authentication'] in ['金V', '红V'] or contribution_dict.get(row['screen_name']) is not None:
    #         if row['created_at'] <= start_time:
    #             tweet_data = row[['id', 'user_id', 'screen_name', 'text', 'attitudes_count', 'comments_count', 'reposts_count']].copy()
    #             tweet_data['round'] = -1
    #             tweets = pd.concat([tweets, tweet_data.to_frame().T], ignore_index=True)

    # tweets.to_csv(previous_tweets_path, index=False, encoding='utf-8')




                


            


