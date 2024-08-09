import time
from tqdm import tqdm
import pandas as pd, numpy as np
from datetime import datetime
import helpers
from importlib import reload
reload(helpers)

today_date = datetime.today().strftime('%Y-%m-%d')
today_date = '2024-07-16'

df = pd.read_csv(f's03_crawled_news.{today_date}.csv', index_col=0)

translation_model_name = "VietAI/envit5-translation"
# df['content_en'] = helpers.translate_batch_vi_en(text_list=df['content'], batch_size=1, to_en=True)
# local 38-47min for 127 news

# df['content_en'] = helpers.translate_pipeline_batch(df['content'].tolist(), max_length=2000, model_name=translation_model_name, batch_size=4)
# 172s for 4 article, max_length 2000
# same with using translate_pipeline of 4 article
df['content_en'] = [''.join(helpers.translate_pipeline(helpers.split_article_into_parts(content, max_length=512), model_name=translation_model_name, max_length=512)) for content in tqdm(df['content'].tolist())]
# 25s/it


# a = time.time()
# helpers.translate_pipeline(helpers.split_article_into_parts(df['content'].head().tolist()[0], max_length=512), model_name=translation_model_name, max_length=512)
# print(time.time()-a)
# chunking and translate using pipeline, chunk size 200 >> 48s
# chunking and translate using pipeline, chunk size 512 >> 48s

# a = time.time()
# helpers.translate(text, model_name=translation_model_name, max_length=len(text)/3.5/0.9)
# print(time.time()-a)
# # 71s

# a = time.time()
# helpers.translate_batch_vi_en([text], model_name=translation_model_name, to_en=True, max_length=len(text)/3.5/0.9,)
# print(time.time()-a)
# # 72s 
df.to_csv(f's04_translate_content.{today_date}.csv')


#
df = pd.read_csv(f's04_translate_content.{today_date}.csv', index_col=0)

# Initialize the zero-shot summarization pipeline

# classification_model_name = "facebook/bart-large-mnli"
# categories = ["product", "legal", "market trend", "business update", "technology innovation", 'antifraud', 'credit scoring']

# df['content_summarize']

# summarization_model_name = "VietAI/vit5-base-vietnews-summarization"
# df['content_summarize'] = 
# test_sum = [helpers.summarize_pipeline(x, model_name=summarization_model_name, max_length=200, min_length=100) for x in tqdm(df['content'].head(5).tolist())]

# df['content'].head(5).tolist()[i], '\n\n',  test_sum[i]
# SHIT MODEL

# try english model
summarization_model_name = "facebook/bart-large-cnn"
df['content_summarize_en'] = [''.join(helpers.summarize_pipeline(helpers.split_article_into_parts(x, 3000), model_name=summarization_model_name, max_length=100, min_length=50)) for x in tqdm(df['content_en'].tolist())]
df['content_summarize_en'] = df['content_summarize']
del df['content_summarize']
# i = 0
# print(df['content_en'].head(5).tolist()[i], '\n\n',  test_sum[i])

df.to_csv(f's04_summarize_content.{today_date}.csv')

