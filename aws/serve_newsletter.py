import boto3
import json
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ['NEWSLETTER_BUCKET']

def lambda_handler(event, context):
    try:
        # Get the newsletter filename from the query string
        newsletter_name = event['queryStringParameters']['name']
        
        # Retrieve the newsletter from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=newsletter_name)
        newsletter_content = response['Body'].read().decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/markdown',
                'Access-Control-Allow-Origin': '*'
            },
            'body': newsletter_content
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }