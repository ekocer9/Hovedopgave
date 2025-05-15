import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlparse, urlunparse
import sqlite3

# Database connection
DB_PATH = r'C:\Users\enes0\Coding\Hovedopgave\Hovedopgave\Backend\database\anime_merchandise.db'

def is_image_link(url):
    try:
        path = urlsplit(url).path
        return any(path.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"])
    except Exception:
        return False

def normalize_product_url(url):
    parsed = urlparse(url)
    parts = parsed.path.lower().strip("/").split("/")
    if "products" in parts:
        i = parts.index("products")
        if i + 1 < len(parts):
            path = "/products/" + parts[i + 1]
        else:
            path = parsed.path
    else:
        path = parsed.path
    return urlunparse((parsed.scheme, parsed.netloc, path, '', '', ''))

def normalize_collection_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.split('?')[0], '', '', ''))

def save_crawled_data(urls):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for url in urls:
        normalized_url = normalize_product_url(url)
        cursor.execute("SELECT 1 FROM crawled WHERE url = ?", (normalized_url,))
        if cursor.fetchone():
            print(f"URL already exists, skipping: {normalized_url}")
        else:
            try:
                cursor.execute("INSERT INTO crawled (url) VALUES (?)", (normalized_url,))
                print(f"Saved crawled URL: {normalized_url}")
            except sqlite3.IntegrityError:
                print(f"Duplicate URL skipped: {normalized_url}")
    conn.commit()
    conn.close()

def crawl_products_from_collection(collection_url, base_url, visited_collections):
    normalized = normalize_collection_url(collection_url)
    if normalized in visited_collections:
        print(f"Already visited collection: {collection_url}, skipping.")
        return []
    visited_collections.add(normalized)

    try:
        response = requests.get(collection_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        product_links = []
        nested_collections = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)

            if is_image_link(full_url) or any(social in href for social in ["facebook", "twitter", "pinterest"]):
                continue
            if "exclusive" in href.lower() or "member" in href.lower():
                continue
            if "/products/" in href and full_url not in product_links:
                product_links.append(full_url)
            elif "/collections/" in href and "/products/" not in href:
                norm_nested = normalize_collection_url(full_url)
                if norm_nested not in visited_collections:
                    nested_collections.append(full_url)

        print(f"Found {len(product_links)} products in collection: {collection_url}")
        save_crawled_data(product_links)

        for nested in nested_collections:
            crawl_products_from_collection(nested, base_url, visited_collections)

    except requests.exceptions.RequestException as e:
        print(f"Error crawling collection {collection_url}: {e}")

def crawl_collections(base_url, visited_collections):
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        found = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/collections/" in href:
                full_url = urljoin(base_url, href)
                norm = normalize_collection_url(full_url)
                if norm not in visited_collections:
                    found.append(full_url)

        print(f"Found {len(found)} collections on homepage: {base_url}")

        for col in found:
            crawl_products_from_collection(col, base_url, visited_collections)

    except requests.exceptions.RequestException as e:
        print(f"Error crawling homepage {base_url}: {e}")

if __name__ == "__main__":
    websites_file = "websites.txt"
    visited_collections = set()

    try:
        with open(websites_file, "r") as f:
            websites = [line.strip() for line in f if line.strip().startswith(("http://", "https://"))]
        for url in websites:
            print(f"Starting crawl for: {url}")
            crawl_collections(url, visited_collections)
    except FileNotFoundError:
        print(f"File not found: {websites_file}")
