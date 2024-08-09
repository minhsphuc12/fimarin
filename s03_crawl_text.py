import time
import pandas as pd, numpy as np
from datetime import datetime
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

today_date = datetime.today().strftime('%Y-%m-%d')
today_date = '2024-07-16'

classified_df = pd.read_csv(f's02_classified_news.{today_date}.csv', index_col=0)
filtered_df = classified_df[classified_df['category']!='other']

# def fetch_article_content(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)  # Use headless=False to see the browser
#         page = browser.new_page()

#         # Go to the specified URL
#         page.goto(url, wait_until='domcontentloaded')

#         page = browser.new_page()

#         # Navigate to the article URL
#         page.goto(url, wait_until='domcontentloaded')

#         # Optional: Wait for the specific content to ensure it is loaded
#         page.wait_for_selector('.sc-longform-header')

#         # Scrape the full article content
#         # Example: Fetching the full text from within <p> tags, modify as needed based on actual content structure
#         article_content = page.query_selector_all('p')
#         full_text = ' '.join([p.text_content() for p in article_content if p.text_content()])

#         # Close the browser
#         # browser.close()

#     return full_text


# filtered_df['content2'] = filtered_df['url'].map(fetch_article_content)


nest_asyncio.apply()

async def fetch_article_content(url, semaphore):
    async with semaphore:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, wait_until='domcontentloaded')
            await page.wait_for_selector('.sc-longform-header')

            # Scrape the full article content
            article_content = await page.query_selector_all('p')
            full_text = ' '.join([await p.text_content() for p in article_content if await p.text_content()])

            await browser.close()
            return full_text

async def fetch_all_contents(urls, max_concurrent_tasks=3):
    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    tasks = [fetch_article_content(url, semaphore) for url in urls]
    return await asyncio.gather(*tasks)

async def main():
    urls = filtered_df['url'].tolist()
    contents = await fetch_all_contents(urls)
    filtered_df['content'] = contents

    # Save or further process the dataframe as needed
    # filtered_df.to_csv(f'completed_news.{today_date}.csv')

# Run the main function using asyncio
a = time.time()
asyncio.run(main())
print(time.time() - a)

filtered_df['date'] = pd.to_datetime(filtered_df['content'].map(lambda x: x.split(' ')[2]))

filtered_df.to_csv(f's03_crawled_news.{today_date}.csv')