from tqdm import tqdm
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from utils import insert_to_mongodb

from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_news_item(link, cutoff_date):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(link)
            
            # Extract date
            date_element = page.query_selector(".format_date")
            if date_element:
                date_str = date_element.inner_text().strip()
                news_date = datetime.strptime(date_str, "%d/%m/%Y")
                
                if news_date < cutoff_date:
                    return None
                
                # Extract title
                title = page.query_selector('h1.article-detail-title').inner_text().strip()
                # Extract subtitle
                subtitle = page.query_selector(".article-detail-desc").inner_text().strip()
                # Extract content
                content_elements = page.query_selector_all(".__MASTERCMS_CONTENT p")
                content = "\n".join([el.inner_text().strip() for el in content_elements])
                
                return {
                    "title": title,
                    "subtitle": subtitle,
                    "date": date_str,
                    "link": f"https://thoibaonganhang.vn{link}",
                    "content": content
                }
    except Exception as e:
        print(f"Failed to process link {link}: {e}")
        return None

def crawl_thoibaonganhang(days=7, num_threads=4):
    news_items = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the main page
        page.goto("https://thoibaonganhang.vn/")
        
        # Extract news links from the main page
        news_links = page.query_selector_all("a.article-link")
        links = [link.get_attribute("href") for link in news_links]
        
        browser.close()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fetch_news_item, link, cutoff_date): link for link in links}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                news_items.append(result)
    
    return news_items

def main():
    news_items = crawl_thoibaonganhang()
    len(news_items)
    # Prepare data for MongoDB insertion
    for item in news_items:
        item['domain'] = 'https://thoibaonganhang.vn/'
        item['summary'] = item.pop('subtitle')
        item['url'] = item.pop('link')

    # Insert data into MongoDB
    insert_to_mongodb(news_items, "thoibaonganhang")

if __name__ == "__main__":
    main()