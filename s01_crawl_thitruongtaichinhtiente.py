from datetime import datetime
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
from helpers import insert_article_to_mongodb, check_url_exists_in_mongodb
from tqdm import tqdm

urls = [
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/san-pham-dich-vu',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/chinh-sach-moi',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/tin-hiep-hoi-ngan-hang',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/tin-hoi-vien',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te/nghien-cuu-trao-doi',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te/van-de-nhan-dinh',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/nghiep-vu-tai-chinh-ngan-hang',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/hoi-dap',
    'https://thitruongtaichinhtiente.vn/cong-nghe',
]

def get_article_links(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_selector(".b-grid")
        
        article_links = []
        for article in page.query_selector_all('.b-grid'):
            headline_element = article.query_selector('.b-grid__title > a')
            content_element = article.query_selector('.b-grid__desc > a')
            
            if headline_element and content_element:
                title = headline_element.text_content()
                subtitle = content_element.text_content()
                article_url = headline_element.get_attribute('href')
                article_links.append((title, subtitle, article_url))
        
        browser.close()
    return article_links

def process_article(article_info):
    title, subtitle, article_url = article_info
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(article_url, wait_until='domcontentloaded', timeout=10000)
            
            if check_url_exists_in_mongodb(article_url, 'articles', db_name='news', 
                                           non_null_fields=['title', 'content', 'date', 'title']):
                print(f"Article {article_url} already exists in MongoDB. Skipping...")
                return None

            article_content = page.query_selector_all('.c-news-detail p')
            content = " ".join([p.text_content() for p in article_content])

            date_element = page.query_selector('.sc-longform-header-date')
            if date_element:
                date_str = date_element.text_content().strip()
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y - %H:%M")
                except ValueError:
                    date_obj = datetime.now()
            else:
                date_obj = datetime.now()

            return {
                'title': title,
                'subtitle': subtitle,
                'url': article_url,
                'content': content,
                'date': date_obj,
                'domain': 'https://thitruongtaichinhtiente.vn'
            }
        except Exception as e:
            print(f"Error processing article {article_url}: {str(e)}")
            return None
        finally:
            browser.close()

def main():
    # Stage 1: Get article links from all URLs
    all_article_links = []
    for url in urls:
        article_links = get_article_links(url)
        all_article_links.extend(article_links)
        print(f"Fetched {len(article_links)} links from: {url}")
    
    print(f"Total articles found: {len(all_article_links)}")

    # Mass check against MongoDB
    new_article_links = []
    for title, subtitle, url in tqdm(all_article_links, desc="Checking MongoDB"):
        if not check_url_exists_in_mongodb(url, 'articles', db_name='news', 
                                           non_null_fields=['title', 'content', 'date']):
            new_article_links.append((title, subtitle, url))
    
    print(f"New articles to process: {len(new_article_links)}")

    # Stage 2: Process articles and insert into MongoDB
    with ThreadPoolExecutor(max_workers=4) as executor:
        articles = []
        for result in tqdm(executor.map(process_article, new_article_links), 
                           total=len(new_article_links), 
                           desc="Processing articles"):
            if result:
                articles.append(result)

    # Insert data into MongoDB
    insert_article_to_mongodb(articles, db_name='news', collection_name='articles')
    print(f"Inserted {len(articles)} articles into MongoDB")

if __name__ == "__main__":
    main()