import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl_website(base_url):
    """
    Crawl a website to find product page URLs.

    Args:
        base_url (str): The base URL of the website to crawl.

    Returns:
        list: A list of discovered product URLs.
    """
    try:
        # Fetch the HTML content of the base URL
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.text, "html.parser")

        product_links = []

        # Find all links on the page
        for link in soup.find_all("a", href=True):
            href = link["href"]
            
            # Filter links to include only product pages (customize as needed)
            if "catalogue/" in href and href.endswith("/index.html"):
                full_url = urljoin(base_url, href)  # Handle relative URLs
                if full_url not in product_links:  # Avoid duplicates
                    product_links.append(full_url)

        print(f"Found {len(product_links)} product links on {base_url}")
        return product_links

    except requests.exceptions.RequestException as e:
        print(f"Error crawling {base_url}: {e}")
        return []

def crawl_multiple_websites(file_path):
    """
    Crawl multiple websites listed in a file.

    Args:
        file_path (str): Path to the file containing website URLs.

    Returns:
        dict: A dictionary with website URLs as keys and their product links as values.
    """
    results = {}

    try:
        with open(file_path, "r") as file:
            websites = [line.strip() for line in file if line.strip()]  # Read non-empty lines

        for website in websites:
            print(f"Starting crawl for {website}")
            product_links = crawl_website(website)
            results[website] = product_links

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    return results

# Example usage
if __name__ == "__main__":
    # Path to the file containing website URLs
    file_path = "websites.txt"
    results = crawl_multiple_websites(file_path)

    # Print the results
    for website, product_links in results.items():
        print(f"\nWebsite: {website}")
        for link in product_links:
            print(link)
