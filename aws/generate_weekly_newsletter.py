import boto3
from datetime import datetime, timedelta
from openai import OpenAI
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    s3 = boto3.client('s3')

    # Extract articles from DynamoDB
    seven_days_ago = datetime.now() - timedelta(days=7)
    response = table.scan(
        FilterExpression='#date >= :seven_days_ago',
        ExpressionAttributeNames={'#date': 'date'},
        ExpressionAttributeValues={':seven_days_ago': seven_days_ago.isoformat()}
    )
    articles = response['Items']

    # Generate newsletter
    newsletter_content = generate_newsletter(articles)

    # Save newsletter to S3
    bucket_name = os.environ['NEWSLETTER_BUCKET']
    file_name = f'weekly_newsletter_{datetime.now().strftime("%Y%m%d")}.md'
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=newsletter_content)

    return {
        'statusCode': 200,
        'body': f'Newsletter generated and saved to S3: {file_name}'
    }

def generate_newsletter(articles):
    # Group articles by category
    grouped_articles = group_articles_by_category(articles)
    
    client = OpenAI()
    newsletter_content = "# Nội dung\n\n"

    datanest_categories = [
        'Credit and Loan Products',
        'Unsecured Loan Market Trends',
        # ... (other categories)
    ]

    for category, category_articles in grouped_articles.items():
        if category not in datanest_categories:
            continue

        article_info = "\n".join([f"- Title: {article['title']}\n  Subtitle: {article.get('subtitle', 'N/A')}\n  Summary: {article.get('summary', 'N/A')}\n  URL: {article.get('url', 'N/A')}" for article in category_articles])

        prompt = f"""
        Generate a newsletter section for the '{category}' category. Focus on the most important and impactful news from the past week.

        OUTPUT FORMAT SHOULD BE:
        - CATEGORY (in vietnamese, bold, header 2)
        - News 1
        - News ...
        - News n
        - Section Line breaker

        Each news item should be formatted as:
        Title (in bold, Vietnamese, header 3)
        Summary (in Vietnamese)
        Đọc thêm: <URL>

        You need to stay in markdown format

        Summarize key points, highlight trends, and provide insights. Use the following article information:

        {article_info}

        News included in the newsletter should be relevant to the context of our company Datanest: Datanest is credit scoring company that provide credit score and potential customer leads from telco data, clients are banks and other financial institutions in Vietnam, Datanest care about data privacy, security and accuracy of the data, and all related news about the process of unsecured loan applications. 
        
        Your response should be well-structured, engaging, and informative. Aim for about 200-300 words per category.
        Include the URL after mentioning each news item.

        Target audience: internal members of Datanest, potential investors, and other stakeholders.

        REMEMBER, THE OUTPUT MUST BE IN VIETNAMESE.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a skilled news editor creating a weekly newsletter."},
                {"role": "user", "content": prompt}
            ]
        )

        newsletter_content += response.choices[0].message.content + "\n\n"

    # Generate executive summary (implementation remains the same)

    return newsletter_content

def group_articles_by_category(articles):
    grouped = {}
    for article in articles:
        category = article.get('category', 'Uncategorized')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(article)
    return grouped

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))