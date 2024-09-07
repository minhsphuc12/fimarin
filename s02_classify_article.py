from importlib import reload
from tqdm import tqdm
import time
from datetime import datetime, timedelta
import pandas as pd, numpy as np
from pymongo import MongoClient
import torch
import helpers
reload(helpers)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['news']
collection = db['articles']

# Get articles from the last seven days with null category
seven_days_ago = datetime.now() - timedelta(days=7)
query = {
    'date': {'$gte': seven_days_ago},
    'category': {'$exists': False}
}
articles = list(collection.find(query))

# Convert articles to pandas DataFrame
df = pd.DataFrame(articles)

# Prepare title_subtitle field
df['title_subtitle'] = df['title'] + ' #:# ' + df['subtitle']

# Translate
translation_model_name = "VietAI/envit5-translation"
df['title_subtitle_en'] = helpers.translate_batch(('vi:' + df['title_subtitle']).to_list(), model_name=translation_model_name, batch_size=20)

# Classification
classify_model_name = 'facebook/bart-large-mnli'

# categories = ["banking", 'credit scoring', "financial regulation", "market analysis", "investment news", 'technology innovation', 'fintech', 'cryptocurrency', 'blockchain', 'law and finance', 'financial technology', 'digital banking', 'online lending', 'mobile payments', 'financial inclusion', 'risk management', 'compliance', 'financial literacy', 'economic trends', 'financial markets']


categories = ['Monetary Policy and Central Bank Updates',
'Banking Regulations and Compliance',
'Interest Rate Changes',
'Economic Indicators and Market Trends',
'Credit and Loan Products',
'Unsecured Loan Market Trends',
'Digital Banking Innovations',
'Fintech Developments',
'Cybersecurity in Finance',
'Data Privacy and Protection in Banking',
'Credit Scoring and Risk Assessment',
'Consumer Credit Trends',
'Banking Mergers and Acquisitions',
'Financial Institution Performance Reports',
'Customer Experience and Service Improvements',
'Mobile and Online Banking',
'Personal Finance and Wealth Management',
'Investment Banking News',
'Retail Banking Trends',
'Payment Systems and Digital Currencies',
'Fraud and Anti-Money Laundering (AML)',
'Financial Inclusion Initiatives',
'Sustainability and Green Finance',
'Economic Recovery and Stimulus Measures',
'Startups and Venture Capital in Finance',
'Market and Stock Exchange News',
'Corporate Lending and Business Financing',
'Real Estate and Mortgage Markets',
'International Banking and Finance News',
'Emerging Technologies (AI, Blockchain) in Finance']

results = helpers.classify_text_batch_pipeline(texts=df['title_subtitle_en'].tolist(), categories=categories, model_name=classify_model_name, batch_size=4)

df['category'] = [r['category'] for r in results]
df['tags'] = [r['tags'] for r in results]

# Update MongoDB with new fields
for index, row in df.iterrows():
    collection.update_one(
        {'_id': row['_id']},
        {'$set': {
            'title_subtitle': row['title_subtitle'],
            'title_subtitle_en': row['title_subtitle_en'],
            'category': row['category'],
            'tags': row['tags']
        }}
    )

print(f"Classification completed and database updated {df.shape[0]} articles")

# Optional: Display results
print(df.groupby('category').agg(count=('_id', 'count')).reset_index())
print("\nSample of categories and tags:")
print(df[['category', 'tags']].head())

# filter then save to batch to crawl full content
df.groupby('category').agg(count=('url', 'count')).reset_index()

# df.to_csv(f's02_classified_news.{datetime.today().strftime("%Y-%m-%d")}.csv')

