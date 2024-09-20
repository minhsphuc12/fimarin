import boto3
import os
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = os.environ['NEWSLETTER_BUCKET']

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='weekly_newsletter_')
    
    newsletters = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.md')]
    newsletters.sort(reverse=True)  # Sort in descending order (most recent first)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({'newsletters': newsletters})
    }