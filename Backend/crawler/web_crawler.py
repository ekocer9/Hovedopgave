import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3

# Database connection
DB_PATH = r'C:\Users\Enes\Coding\Hovedopgave\Backend\database\anime_merchandise.db'  # Adjust path if needed

def save_crawled_data(urls, collection_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for url in urls:
        cursor.execute("SELECT 1 FROM crawled WHERE url = ?", (url,))
        if cursor.fetchone():
            print(f"URL already exists, skipping: {url}")
        else:
            try:
                cursor.execute("""
                    INSERT INTO crawled (url, collection_name, status)
                    VALUES (?, ?, ?)
                """, (url, collection_name, 'pending'))
                print(f"Saved crawled URL: {url}")
            except sqlite3.IntegrityError:
                print(f"Duplicate URL skipped: {url}")

    conn.commit()
    conn.close()

def crawl_products_from_collection(collection_url, base_url, collection_name, visited_collections):
    """
    Crawl all product links within a specific collection and save them to the database.
    
    Args:
        collection_url (str): The URL of the collection page.
        base_url (str): The base URL of the website.
        collection_name (str): The name of the collection.
        visited_collections (set): A set of already visited collection URLs.

    Returns:
        list: A list of product URLs.
    """
    if collection_url in visited_collections:
        print(f"Already visited collection: {collection_url}, skipping.")
        return []

    try:
        response = requests.get(collection_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Mark this collection as visited
        visited_collections.add(collection_url)

        product_links = []
        collection_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            # Exclude social sharing or irrelevant links
            if any(social in href for social in ["pinterest.com", "facebook.com", "twitter.com"]):
                continue

             # Exclude image links
            if any(href.lower().endswith(ext) for ext in [".jpg", ".png", ".gif", ".jpeg", ".webp"]):
                print(f"Skipping image link: {full_url}")
                continue

            # Detect product links with flexible logic
            if "/products/" in href:
                if full_url not in product_links:
                    product_links.append(full_url)

            # Detect collection links but avoid product URLs
            elif "/collections/" in href and not "/products/" in href:
                if full_url not in visited_collections:
                    collection_links.append(full_url)

        print(f"Found {len(product_links)} products in collection: {collection_url}")
        save_crawled_data(product_links, collection_name)

        # Recursively crawl nested collections
        for nested_collection in collection_links:
            crawl_products_from_collection(nested_collection, base_url, collection_name, visited_collections)

        return product_links

    except requests.exceptions.RequestException as e:
        print(f"Error crawling collection {collection_url}: {e}")
        return []

def crawl_collections(base_url):
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        collection_links = []
        visited_collections = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/collections/" in href:
                full_url = urljoin(base_url, href)
                if full_url not in collection_links:
                    collection_links.append(full_url)

        print(f"Found {len(collection_links)} collections on homepage: {base_url}")

        for collection_url in collection_links:
            collection_name = collection_url.split("/")[-1]
            crawl_products_from_collection(collection_url, base_url, collection_name, visited_collections)

    except requests.exceptions.RequestException as e:
        print(f"Error crawling homepage {base_url}: {e}")

if __name__ == "__main__":
    websites_file = "websites.txt"

    try:
        with open(websites_file, "r") as file:
            websites = [
                line.strip()
                for line in file
                if line.strip() and (line.startswith("http://") or line.startswith("https://"))
            ]

        for base_url in websites:
            print(f"Starting crawl for: {base_url}")
            crawl_collections(base_url)

    except FileNotFoundError:
        print(f"File not found: {websites_file}")
