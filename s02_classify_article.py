import pandas as pd, numpy as np
from datetime import datetime
# for loop to read all crawled title from all sources today
page = 'thitruongtaichinhtiente.vn'
today_date = datetime.today().strftime('%Y-%m-%d')


df = pd.read_csv(f'{page}.{today_date}.csv', index_col=0).drop_duplicates(['url'])
df['title_subtitle'] = df['title'] + ' #:# ' + df['subtitle']

# classify by keyword
# - flag
keywords = ['tín dụng', 'tiêu dùng', 'điểm', 'chính sách', 'sản phẩm', 'thẻ tín dụng']
df['relevant'] = df['title_subtitle'].apply(lambda x: any(keyword.lower() in x.lower() for keyword in keywords))
df['relevant'].sum()

# classify by model
# - label: manual
# - model: small 

# filter then save to batch to crawl full content
relevant_df = df[df['relevant']]

relevant_df.to_csv(f'filtered_news.{today_date}.csv')
