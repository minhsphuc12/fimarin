from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from utils import insert_to_mongodb

def crawl_thoibaonganhang(days=7):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        news_items = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Navigate to the main page
        page.goto("https://thoibaonganhang.vn/")
        
        # Extract news links from the main page
        news_links = page.query_selector_all("a.title")
        links = [link.get_attribute("href") for link in news_links]
        
        for link in links:
            page.goto(f"https://thoibaonganhang.vn{link}")
            
            # Extract date
            date_element = page.query_selector(".date")
            if date_element:
                date_str = date_element.inner_text().strip()
                news_date = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
                
                if news_date < cutoff_date:
                    continue
                
                # Extract title
                title = page.query_selector("h1").inner_text().strip()
                
                # Extract subtitle
                subtitle = page.query_selector(".sapo").inner_text().strip()
                
                # Extract content
                content_elements = page.query_selector_all(".detail-content p")
                content = "\n".join([el.inner_text().strip() for el in content_elements])
                
                news_items.append({
                    "title": title,
                    "subtitle": subtitle,
                    "date": date_str,
                    "link": f"https://thoibaonganhang.vn{link}",
                    "content": content
                })
        
        browser.close()
        
    return news_items

def main():
    news_items = crawl_thoibaonganhang()
    
    # Prepare data for MongoDB insertion
    for item in news_items:
        item['domain'] = 'https://thoibaonganhang.vn/'
        item['summary'] = item.pop('subtitle')
        item['url'] = item.pop('link')

    # Insert data into MongoDB
    insert_to_mongodb(news_items, "thoibaonganhang")

if __name__ == "__main__":
    main()