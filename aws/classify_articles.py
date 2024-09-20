import boto3
from datetime import datetime, timedelta
import os
import helpers
from importlib import reload

reload(helpers)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Get articles from the last seven days with null category
    seven_days_ago = datetime.now() - timedelta(days=7)
    response = table.scan(
        FilterExpression='#date >= :seven_days_ago and attribute_not_exists(category)',
        ExpressionAttributeNames={'#date': 'date'},
        ExpressionAttributeValues={':seven_days_ago': seven_days_ago.isoformat()}
    )
    articles = response['Items']

    # Prepare and classify articles
    for article in articles:
        article['title_subtitle'] = article['title'] + ' #:# ' + article.get('subtitle', '')
        article['title_subtitle_en'] = helpers.translate_batch(['vi:' + article['title_subtitle']], model_name="VietAI/envit5-translation")[0]

    categories = [
        'Monetary Policy and Central Bank Updates',
        'Banking Regulations and Compliance',
        # ... (other categories)
    ]

    classification_results = helpers.classify_text_batch_pipeline(
        texts=[article['title_subtitle_en'] for article in articles],
        categories=categories,
        model_name='facebook/bart-large-mnli',
        batch_size=4
    )

    # Update articles with classification results
    for article, result in zip(articles, classification_results):
        article['category'] = result['category']
        article['tags'] = result['tags']

        # Update DynamoDB
        table.update_item(
            Key={'url': article['url']},
            UpdateExpression='SET category = :category, tags = :tags, title_subtitle = :title_subtitle, title_subtitle_en = :title_subtitle_en',
            ExpressionAttributeValues={
                ':category': article['category'],
                ':tags': article['tags'],
                ':title_subtitle': article['title_subtitle'],
                ':title_subtitle_en': article['title_subtitle_en']
            }
        )

    return {
        'statusCode': 200,
        'body': f'Classified {len(articles)} articles'
    }

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))