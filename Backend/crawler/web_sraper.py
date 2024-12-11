import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time

# Database path
DB_PATH = 'C:/Users/Enes/Coding/Hovedopgave/Backend/database/anime_merchandise.db'

def scrape_product_details(product_url):
    """
    Scrape product details using Selenium for all websites.
    """
    try:
        # Set up Selenium WebDriver
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Open the product URL
        driver.get(product_url)

        # Extract product name
        try:
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            name = name_element.text.strip()
        except Exception as e:
            print(f"Error extracting name for {product_url}: {e}")
            name = "Unknown Product"

        # Extract product price

        try:
            # Try to find the sale price first
            sale_price_element = driver.find_element(By.CSS_SELECTOR, "span.price-item--sale.price-item--last")
            sale_price_text = sale_price_element.text.strip()

            if sale_price_text:
                price = float(sale_price_text.replace("$", "").replace("USD", "").strip())
            else:
                raise ValueError("Sale price text is empty")
        except Exception as e:
            print(f"Sale price not found or failed for {product_url}: {e}")
            try:
                price_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-product-price], .price-item--regular"))
                )
                price_text = price_element.text.strip()
                price = float(price_text.replace("kr", "").replace("$", "").replace(",", "").replace("USD", "").replace("DKK", "").strip())
            except Exception as e:
                print(f"Error extracting price for {product_url}: {e}")
                price = None
                
        # Extract image URL
        try:
            # Attempt to find the image element
            image_element = driver.find_element(By.CSS_SELECTOR, "img[src], img[data-src], img[srcset]")
            driver.execute_script("arguments[0].scrollIntoView();", image_element)
            time.sleep(2)
            image_url = image_element.get_attribute("data-src") or image_element.get_attribute("src") or image_element.get_attribute("srcset")
            
            # Check for fallback in <noscript> tag
            if not image_url:
                noscript_tag = driver.find_element(By.CSS_SELECTOR, "noscript")
                soup = BeautifulSoup(noscript_tag.get_attribute("innerHTML"), "html.parser")
                image_tag = soup.find("img")
                image_url = image_tag["src"] if image_tag else None
            
            # Check Open Graph metadata
            if not image_url:
                og_image = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']")
                image_url = og_image.get_attribute("content")
            
            # Ensure the URL is complete
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url
        except Exception as e:
            print(f"Error extracting image URL for {product_url}: {e}")
            image_url = None

        # Extract product description
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, "div.product-description, meta[name='description']")
            description = description_element.text.strip() if description_element.tag_name == "div" else description_element.get_attribute("content")
        except Exception as e:
            print(f"Error extracting description for {product_url}: {e}")
            description = None

        delivery_options = "Standard Shipping"

        driver.quit()

        return {
            "name": name,
            "price": price,
            "image_url": image_url,
            "description": description,
            "delivery_options": delivery_options,
            "product_url": product_url,
        }
    except Exception as e:
        print(f"Error scraping product with Selenium: {product_url}: {e}")
        return None

def scrape_all_products():
    """
    Scrape all products marked as 'pending' in the `crawled` table and save them to the `products` table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch unscraped products from the `crawled` table
    cursor.execute("""
        SELECT c.id, c.url
        FROM crawled c
        LEFT JOIN products p ON c.url = p.product_url
        WHERE c.status = 'pending' AND p.product_url IS NULL
    """)
    crawled_data = cursor.fetchall()

    for crawl_id, product_url in crawled_data:
        print(f"Scraping product: {product_url}")
        details = scrape_product_details(product_url)

        # Validate the scraped details
        if details and details["name"] and details["price"] is not None:
            try:
                # Check if the product URL is already in the `products` table
                cursor.execute("SELECT 1 FROM products WHERE product_url = ?", (details["product_url"],))
                if cursor.fetchone():
                    print(f"Product already scraped: {details['product_url']}")
                    continue

                # Save the product details into the `products` table
                cursor.execute("""
                    INSERT INTO products (name, price, image_url, description, delivery_options, product_url, source_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    details["name"], 
                    details["price"], 
                    details["image_url"], 
                    details["description"], 
                    details["delivery_options"], 
                    details["product_url"], 
                    crawl_id
                ))
                print(f"Saved product {crawl_id} in the database.")
            except sqlite3.IntegrityError as e:
                print(f"Failed to save product {crawl_id}: {e}")
        else:
            print(f"Skipping product due to missing or invalid data: {details}")

        time.sleep(2)  # Delay between requests

    conn.commit()
    conn.close()

if __name__ == "__main__":
    try:
        scrape_all_products()
    except KeyboardInterrupt:
        print("Script interrupted. Saving progress...")
