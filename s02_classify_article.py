from tqdm import tqdm
from transformers import pipeline
import time
import pandas as pd, numpy as np
from datetime import datetime
import torch
# for loop to read all crawled title from all sources today
page = 'thitruongtaichinhtiente.vn'
today_date = datetime.today().strftime('%Y-%m-%d')
today_date = '2024-07-16'

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

# translate 
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
model_name = "VietAI/envit5-translation"
tokenizer = AutoTokenizer.from_pretrained(model_name)  
translator = AutoModelForSeq2SeqLM.from_pretrained(model_name)
from transformers.tokenization_utils import PreTrainedTokenizer

def translate_model(text_list, translator, tokenizer:PreTrainedTokenizer):
    outputs = translator.generate(tokenizer(text_list, return_tensors="pt", padding=True).input_ids, max_length=512)
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)

def translate_model(text_list, translator, tokenizer:PreTrainedTokenizer, batch_size=8):
    """
    text_list (list): List of texts to be translated.
    translator: Translation model.
    tokenizer: Tokenizer for the model.
    batch_size (int): Number of texts to process in each batch.
    list: List of translated texts.
    """
    translated_texts = []
    # Process the text list in batches
    for i in range(0, len(text_list), batch_size):
        batch_texts = text_list[i:i + batch_size]
        inputs = tokenizer(batch_texts, return_tensors="pt", padding=True)
        outputs = translator.generate(inputs.input_ids, max_length=512)
        translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        translated_texts.extend(translations)
    return translated_texts

a = time.time()
df['title_subtitle_en'] = translate_model(df['title_subtitle'].to_list(), translator=translator, tokenizer=tokenizer, batch_size=20)
print(time.time()-a)


def classify_model(text, classifier, categories):
    result = classifier(text, candidate_labels=categories)
    return result['labels'][0]

categories = ["product", 'credit scoring', "legal", "market trend", "business update", 'technology innovation', 'other']
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
df['category'] = [classify_model(text, classifier=classifier, categories=categories) for text in tqdm(df['title_subtitle_en'].to_list())]

df[['title', 'category']]


# filter then save to batch to crawl full content
df.groupby('category').agg(count=('url', 'count')).reset_index()
relevant_df = df[df['relevant']]
relevant_df.groupby('category').agg(count=('url', 'count')).reset_index()

relevant_df.to_csv(f'filtered_news.{today_date}.csv')
