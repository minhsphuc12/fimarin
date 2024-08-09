from importlib import reload
from tqdm import tqdm
import time
import pandas as pd, numpy as np
from datetime import datetime
import torch
import helpers
reload(helpers)

# for loop to read all crawled title from all sources today
page = 'thitruongtaichinhtiente.vn'
today_date = datetime.today().strftime('%Y-%m-%d')
today_date = '2024-07-16'

df = pd.read_csv(f'{page}.{today_date}.csv', index_col=0).drop_duplicates(['url'])
df['title_subtitle'] = df['title'] + ' #:# ' + df['subtitle']

# classify by keyword
# keywords = ['tín dụng', 'tiêu dùng', 'điểm', 'chính sách', 'sản phẩm', 'thẻ tín dụng']
# df['relevant'] = df['title_subtitle'].apply(lambda x: any(keyword.lower() in x.lower() for keyword in keywords))
# df['relevant'].sum()

# translate 
translation_model_name = "VietAI/envit5-translation"

# translate using transfomers tokenizer in batch to reduce work load 
a = time.time()
df['title_subtitle_en'] = helpers.translate_batch(('vi:' + df['title_subtitle']).to_list(), model_name=translation_model_name, batch_size=20)
print(time.time()-a)
# best result comes with batch size 20

helpers.translate_pipeline(['en: I want to go out tonight'], model_name=translation_model_name)

# classification
classify_model_name = 'facebook/bart-large-mnli'

categories = ["product", 'credit scoring', "legal", "market trend", "business update", 'technology innovation', 'other']

# directly apply pipeline to classify
df['category'] = [helpers.classify_text(text, model_name=classify_model_name, categories=categories) 
                  for text in tqdm(df['title_subtitle'].to_list())]

# 10s/it
# done in ?? min

# using multithreading while apply pipeline parralel classification 
reload(helpers)

df['category'] = helpers.classify_text_batch_pipeline(texts=df['title_subtitle'].tolist(), model_name=classify_model_name, categories=categories, batch_size=4)

# best with batch 4 vietnamese
# completed in 8 min (3s/it)

helpers.classify_text_batch_pipeline(texts=('vi:' + df['title_subtitle']).head(8).tolist(), model_name=classify_model_name, categories=categories, batch_size=4)
# using direct model without translation is not helpful 
#        category  count
# 0         legal      1
# 1  market trend      1
# 2         other    208
# 3       product      6

df['category'] = helpers.classify_text_batch_pipeline(texts=df['title_subtitle_en'].tolist(), model_name=classify_model_name, categories=categories, batch_size=4)

# classify from english is faster (3 min, 1.2s/it)
# with translation have more success
#                 category  count
# 0        business update     15
# 1         credit scoring      2
# 2                  legal     17
# 3           market trend     31
# 4                  other     94
# 5                product     40
# 6  technology innovation     17


# using multithreading with transformer tokenizer
df['cateogry'] = helpers.classify_texts_batch(texts=df['title_subtitle'].tolist(), model_name=classify_model_name, categories=categories, batch_size=20)
# batch size expect 20 min ~ 8s/it

# check result
df[['title_subtitle', 'category']]

# filter then save to batch to crawl full content
df.groupby('category').agg(count=('url', 'count')).reset_index()

df.to_csv(f's02_classified_news.{today_date}.csv')

