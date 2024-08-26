from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import pandas as pd
import csv

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
    
    # Convert news_items to a DataFrame
    df = pd.DataFrame(news_items)

    # Rename columns to match the format of s01_crawl_thitruongtaichinhtiente.py
    df = df.rename(columns={'subtitle': 'summary', 'link': 'url'})

    # Add 'domain' column
    df['domain'] = 'https://thoibaonganhang.vn/'

    # Reorder columns
    df = df[['title', 'summary', 'url', 'content', 'domain']]

    today_date = datetime.today().strftime('%Y-%m-%d')
    output_filename = f'thoibaonganhang.{today_date}.csv'

    df.to_csv(output_filename, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8-sig')
    print(f"Crawled {len(df)} news items and saved to {output_filename}")

if __name__ == "__main__":
    main()