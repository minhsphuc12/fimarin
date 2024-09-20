import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from playwright.sync_api import sync_playwright
import os
from concurrent.futures import ThreadPoolExecutor

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    news_items = main()

    for item in news_items:
        try:
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(url)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

    return {
        'statusCode': 200,
        'body': f'Processed {len(news_items)} articles from thitruongtaichinhtiente.vn'
    }

def main():
    urls = [
        'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang',
        'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/san-pham-dich-vu',
        # ... (other URLs)
    ]

    all_article_links = []
    for url in urls:
        article_links = get_article_links(url)
        all_article_links.extend(article_links)

    with ThreadPoolExecutor(max_workers=4) as executor:
        articles = list(filter(None, executor.map(process_article, all_article_links)))

    return articles

# The rest of the functions (get_article_links, process_article) remain the same as in the original file

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))