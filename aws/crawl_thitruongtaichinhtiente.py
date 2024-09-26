import boto3
from botocore.exceptions import ClientError
import os
from crawl_thoibaonganhang import crawl_thoibaonganhang

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    news_items = crawl_thoibaonganhang()

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
        'body': f'Processed {len(news_items)} articles, inserted {inserted_count} new articles from thoibaonganhang.vn'
    }

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))