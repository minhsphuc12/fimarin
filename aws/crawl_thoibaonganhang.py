import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from playwright.sync_api import sync_playwright
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    news_items = crawl_thoibaonganhang()

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
        'body': f'Processed {len(news_items)} articles'
    }

def crawl_thoibaonganhang(days=7):
    news_items = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to the main page
        page.goto("https://thoibaonganhang.vn/")
        
        # Extract news links from the main page
        news_links = page.query_selector_all("a.article-link")
        links = [link.get_attribute("href") for link in news_links]
        
        for url in links:
            item = fetch_news_item(url, cutoff_date)
            if item:
                news_items.append(item)
        
        browser.close()
    
    return news_items

def fetch_news_item(url, cutoff_date):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=10000)
            
            date_element = page.query_selector(".format_date")
            if date_element:
                date_str = date_element.inner_text().strip()
                news_date = datetime.strptime(date_str, "%d/%m/%Y")
                
                if news_date < cutoff_date:
                    return None
                
                title = page.query_selector('h1.article-detail-title').inner_text().strip()
                subtitle = page.query_selector(".article-detail-desc").inner_text().strip()
                content_elements = page.query_selector_all(".__MASTERCMS_CONTENT p")
                content = "\n".join([el.inner_text().strip() for el in content_elements])

                return {
                    "title": title,
                    "subtitle": subtitle,
                    "date": news_date.isoformat(),
                    "url": url,
                    "content": content,
                    "domain": 'https://thoibaonganhang.vn/'
                }
        except Exception as e:
            print(f"Failed to process link {url}: {e}")
            return None
        finally:
            browser.close()

# For local testing
if __name__ == "__main__":
    print(lambda_handler({}, None))