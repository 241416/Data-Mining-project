from snownlp import SnowNLP
import json
def excel_to_csv(path,output_path):
    df = pd.read_excel(path)
    df.to_csv(output_path, index=False)
    return 0

def save_tojson(dataname, filename):
    with open(filename, 'w', encoding='utf-8') as f_ordinary:
        json.dump(dataname, f_ordinary, ensure_ascii=False, indent=4)

# SnowNLP效果不是很好，用gpt3.5-turbo进行情感分析
def sentiment(text):
    s = SnowNLP(text)
    return s.sentiments 