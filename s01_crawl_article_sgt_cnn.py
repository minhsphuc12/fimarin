import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_text_from_link(url, headers):
    print(f"Fetching from: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract text from paragraphs
    paragraphs = soup.find_all('p')
    return ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)


def get_links_from_sgtimes(category_sgt, headers, num_limit):
    full_url = "https://thesaigontimes.vn/" + category_sgt
    
    response = requests.get(full_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('h3', class_='entry-title td-module-title', limit=num_limit)
    href_link = []
    for link in links:
        try:
            href_link.append(link.find('a')['href'])
            time.sleep(1)
        except:
            print("Not Found")

    return href_link

def get_links_from_cnn(category, headers, num_limit):
    full_url = "https://edition.cnn.com" + category
    response = requests.get(full_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for item in soup.find_all('a', class_='container__link', limit=num_limit):
        links.append(item['href'])
        time.sleep(1)

    return [full_url + i for i in links]


def get_texts_from_links_parallel(links, headers):
    # Use ThreadPoolExecutor to run get_text_from_link in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_text_from_link, url, headers): url for url in links}
        results = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Completed fetching from: {url}")
                time.sleep(1)
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
        return results


def run_parallel_processing(links, headers):
    # Get link and texts
    texts = get_texts_from_links_parallel(links, headers)  # This processes links in parallel
    
    # Convert to dataframe
    df = pd.DataFrame.from_dict(dict(zip(links,texts)), orient='index').reset_index()
    df.columns = ['url','txt']
    
    return df


# TEST WITH CNN
category = 'business' # ['business','economy','investing','tech']
category_sgt = 'tai-chinh-ngan-hang' # ['tai-chinh-ngan-hang','kinh-doanh']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
num_limit = 10
links_cnn = get_links_from_cnn(category, headers, num_limit)
links_sgt = get_links_from_sgtimes(category_sgt, headers, num_limit)
df_txt = run_parallel_processing(links_cnn+links_sgt, headers)