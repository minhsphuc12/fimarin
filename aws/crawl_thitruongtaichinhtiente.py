import boto3
from botocore.exceptions import ClientError
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def crawl_thitruongtaichinhtiente():
    url = "https://thitruongtaichinhtiente.vn"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    news_items = []
    for article in soup.find_all('article', class_='story'):
        title = article.find('h3', class_='story__title').text.strip()
        link = article.find('a', class_='story__title')['href']
        date = article.find('span', class_='story__time').text.strip()
        
        news_items.append({
            'title': title,
            'url': link,
            'date': date,
            'source': 'thitruongtaichinhtiente.vn'
        })
    
    return news_items

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    news_items = crawl_thitruongtaichinhtiente()

    inserted_count = 0
    for item in news_items:
        try:
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(url)'
            )
            inserted_count += 1
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

    return {
        'statusCode': 200,
        'body': f'Processed {len(news_items)} articles, inserted {inserted_count} new articles from thitruongtaichinhtiente.vn'
    }

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))