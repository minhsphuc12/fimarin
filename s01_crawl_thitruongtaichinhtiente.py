from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright
from tqdm import tqdm
import csv

# start on given domain, get all links presented with title
# crawl only today news (how?)

page = 'thitruongtaichinhtiente.vn'

urls = [
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/san-pham-dich-vu',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/tin-hiep-hoi-ngan-hang',
    'https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/tin-hoi-vien',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te/nghien-cuu-trao-doi',
    'https://thitruongtaichinhtiente.vn/dien-dan-tai-chinh-tien-te/van-de-nhan-dinh',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/chinh-sach-moi',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/nghiep-vu-tai-chinh-ngan-hang',
    'https://thitruongtaichinhtiente.vn/phap-luat-nghiep-vu/hoi-dap',
    'https://thitruongtaichinhtiente.vn/cong-nghe',

]

# url = urls[4]
# url = 'https://thitruongtaichinhtiente.vn/'

def get_links(url):
    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to the specified URL
        page.goto(url, wait_until='domcontentloaded')
        # print(page.content())
        # Wait for the content to load (if necessary, adjust or add specific waits)

        # Extract data: headlines and contents


        ### TO DO: implement scroll to get more content but unsuccessful
        # page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        # # Optionally, wait for any lazy-loaded content
        # page.keyboard.down('PageDown')
        # page.evaluate('''async () => {
        #         await new Promise((resolve, reject) => {
        #             var totalHeight = 0;
        #             var distance = 5;
        #             var timer = setInterval(() => {
        #                 var scrollHeight = document.body.scrollHeight;
        #                 window.scrollBy(0, distance);
        #                 totalHeight += distance;

        #                 if(totalHeight >= scrollHeight){
        #                     clearInterval(timer);
        #                     resolve();
        #                 }
        #             }, 100);
        #         });
        #     }''')
        # page.wait_for_timeout(6000)  # waits for 1 second

        page.wait_for_selector(".b-grid")
        articles = []
        article_containers = page.query_selector_all('.b-grid')

        for article in tqdm(article_containers):
            
            headline_element = article.query_selector('.b-grid__title > a')
            content_element = article.query_selector('.b-grid__desc > a')
            # publish_date = article.query_selector('.sc-longform-header-date').text_content()

            if headline_element and content_element:
                title = headline_element.text_content()
                subtitle = content_element.text_content()
                article_url = headline_element.get_attribute('href')

                # full_content = fetch_article_content(article_url, browser)

                articles.append({
                    'title': title,
                    'subtitle': subtitle,
                    'url': article_url,
                })

            else:
                print("Some elements were not found for an article, skipping.")
    return articles

def main():
    articles_crawled = {}
    failed_urls = []

    for url in tqdm(urls):
        try:
            articles = get_links(url)
            articles_crawled[url] = articles
        except:
            failed_urls.append(url)

    articles_crawled_parsed = [{'domain': url, **article} for url in articles_crawled.keys() for article in articles_crawled[url]]

    df = pd.DataFrame(articles_crawled_parsed).reset_index(drop=True).drop_duplicates(['url'])

    # Add empty 'content' column to match the format of s01_crawl_thoibaonganhang.py
    df['content'] = ''

    # Rename columns to match the format of s01_crawl_thoibaonganhang.py
    df = df.rename(columns={'subtitle': 'summary'})

    # Reorder columns
    df = df[['title', 'summary', 'url', 'content', 'domain']]

    today_date = datetime.today().strftime('%Y-%m-%d')
    output_filename = f'thitruongtaichinhtiente.{today_date}.csv'

    df.to_csv(output_filename, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8-sig')
    print(f"Crawled {len(df)} news items and saved to {output_filename}")

if __name__ == "__main__":
    main()