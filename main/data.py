import requests
import csv
import os
import time
from dotenv import load_dotenv

load_dotenv()

class TiktokShopApi:
    def __init__(self, x_rapidapi_key: str):
        self.x_rapidapi_key = x_rapidapi_key
        self.host = 'tiktok-shop-us-api.p.rapidapi.com'
        self.base_url = 'https://tiktok-shop-us-api.p.rapidapi.com'
        self.headers = {
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.x_rapidapi_key
        }

    def _request(self, url: str, params=None):
        try:
            res = requests.get(url, headers=self.headers, params=params)
            print(f'Status Code: {res.status_code}')

            res.raise_for_status()

            if not res.text or not res.text.strip():
                print(f'Empty response body for URL: {url}')
                return {}

            return res.json()

        except requests.exceptions.HTTPError as e:
            print(f'HTTP Error: {e} | URL: {url}')
            return {}
        except requests.exceptions.ConnectionError as e:
            print(f'Connection Error: {e}')
            return {}
        except requests.exceptions.Timeout as e:
            print(f'Timeout Error: {e}')
            return {}
        except requests.exceptions.JSONDecodeError as e:
            print(f'JSON Decode Error: {e}')
            return {}

    def search_products(
        self,
        keyword: str,
        page: int = 1
    ):
        url = f'{self.base_url}/api/search'
        params = {
            'q': keyword,
            'page': str(page)
        }
        return self._request(url, params)


# Write search results to CSV based on new API response structure
def write_search_results_to_csv(filename, products):
    fieldnames = [
        'product_id', 'title', 'brand', 'image', 'url',
        'currency', 'price', 'original_price', 'discount',
        'sold', 'rating', 'reviews',
        'seller_id', 'shop_name', 'slug',
        'search_query', 'search_page', 'found_at'
    ]
    file_exists = os.path.exists(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or csvfile.tell() == 0:
            writer.writeheader()
        for product in products:
            writer.writerow({
                'product_id': product.get('product_id'),
                'title': product.get('title'),
                'brand': product.get('brand'),
                'image': product.get('image'),
                'url': product.get('url'),
                'currency': product.get('currency'),
                'price': product.get('price'),
                'original_price': product.get('original_price'),
                'discount': product.get('discount'),
                'sold': product.get('sold'),
                'rating': product.get('rating'),
                'reviews': product.get('reviews'),
                'seller_id': product.get('seller_id'),
                'shop_name': product.get('shop_name'),
                'slug': product.get('slug'),
                'search_query': product.get('search_query'),
                'search_page': product.get('search_page'),
                'found_at': product.get('found_at')
            })


# Read product IDs from CSV
def read_product_ids_from_csv(file_path):
    product_ids = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header
        for row in csvreader:
            if row:
                product_ids.append(row[0])
    return product_ids


# Search a single keyword across pages
def _search_keyword(client, keyword, max_pages, output_csv):
    total = 0
    print(f'Searching products for keyword: "{keyword}"')

    for page in range(1, max_pages + 1):
        print(f'  Fetching page {page}...')
        res = client.search_products(keyword, page) or {}

        if not res.get('success'):
            print(f'  API returned unsuccessful response on page {page}.')
            break

        products = res.get('data', {}).get('products') or []

        if not products:
            print('  No more products found.')
            break

        write_search_results_to_csv(output_csv, products)
        total += len(products)
        print(f'  Written {total} products so far to {output_csv} (page {page}, {len(products)} products)')

        # Each page returns ~30 products (fixed by the API, no count param available).
        # Keep paginating until we hit max_pages or the API returns no products.
        if len(products) < 30:
            print('  Reached last page (fewer than 30 products returned).')
            break
        time.sleep(3)

    print(f'  Done with "{keyword}". Products written: {total}')
    return total


# Main function: iterate over multiple keywords
# Increase max_pages to collect more — each page yields ~30 products.
def collect_data(keywords, api_key, max_pages=10):
    if not keywords:
        print('No keywords entered.')
        return

    # Accept a single string or a list
    if isinstance(keywords, str):
        keywords = [keywords]

    client = TiktokShopApi(api_key)
    output_csv = 'tiktok_search_data.csv'
    grand_total = 0

    for i, keyword in enumerate(keywords):
        keyword = keyword.strip()
        if not keyword:
            continue
        grand_total += _search_keyword(client, keyword, max_pages, output_csv)
        if i < len(keywords) - 1:
            print('Waiting before next keyword...')
            time.sleep(5)

    print(f'All keywords done. Grand total products written: {grand_total}')


if __name__ == '__main__':
    collect_data(
        keywords=['wireless earbuds', 'bluetooth speaker', 'iphone case'],
        api_key=os.getenv("RapidAPIKey"),
        max_pages=10
    )