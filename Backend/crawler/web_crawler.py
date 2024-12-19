import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
from urllib.parse import urlsplit
from urllib.parse import urlparse, urlunparse

# Database connection
DB_PATH = r'C:\Users\Enes\Coding\Hovedopgave\Backend\database\anime_merchandise.db'  # Adjust path if needed

def is_image_link(url):
    """
    Check if a URL points to an image file by inspecting its extension.
    """
    try:
        # Parse URL and remove query parameters
        path = urlsplit(url).path
        return any(path.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"])
    except Exception:
        return False

def normalize_product_url(url):
    """
    Normalize product URL by removing collection-specific paths or query strings.
    Example:
        Input: https://aniqi.com/collections/shirts/products/limited-tee
        Output: https://aniqi.com/products/limited-tee
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")

    # Keep only base URL and /products/... endpoint
    if "products" in path_parts:
        product_index = path_parts.index("products")
        normalized_path = "/".join(path_parts[:product_index + 2])  # Keep up to /products/slug
    else:
        normalized_path = parsed_url.path

    # Reconstruct normalized URL
    normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, normalized_path, "", "", ""))
    return normalized_url

def save_crawled_data(urls):
    """
    Save crawled URLs to the database after normalizing and filtering duplicates.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for url in urls:
        # Normalize URL to remove collection-specific paths
        normalized_url = normalize_product_url(url)

        cursor.execute("SELECT 1 FROM crawled WHERE url = ?", (normalized_url,))
        if cursor.fetchone():
            print(f"URL already exists, skipping: {normalized_url}")
        else:
            try:
                cursor.execute("""
                    INSERT INTO crawled (url) VALUES (?)
                """, (normalized_url,))
                print(f"Saved crawled URL: {normalized_url}")
            except sqlite3.IntegrityError:
                print(f"Duplicate URL skipped: {normalized_url}")

    conn.commit()
    conn.close()

def crawl_products_from_collection(collection_url, base_url, visited_collections):
    """
    Crawl all product links within a specific collection and save them to the database.

    Args:
        collection_url (str): The URL of the collection page.
        base_url (str): The base URL of the website.
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
            if is_image_link(full_url):
                print(f"Skipping image link: {full_url}")
                continue

            if "exclusive" in href.lower() or "member" in href.lower():
                print(f"Skipping member-exclusive product: {full_url}")
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
        save_crawled_data(product_links)

        # Recursively crawl nested collections
        for nested_collection in collection_links:
            crawl_products_from_collection(nested_collection, base_url, visited_collections)

        return product_links

    except requests.exceptions.RequestException as e:
        print(f"Error crawling collection {collection_url}: {e}")
        return []

def crawl_collections(base_url):
    """
    Start crawling the collections from the homepage.
    """
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
            crawl_products_from_collection(collection_url, base_url, visited_collections)

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
