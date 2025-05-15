import sqlite3
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
import json

from categories import PRODUCT_CATEGORIES


# Database path
DB_PATH = r'C:\Users\enes0\Coding\Hovedopgave\Hovedopgave\Backend\database\anime_merchandise.db'

def normalize_url(url):
    """
    Ensure the URL is complete, converting protocol-relative URLs (//...) to https://...
    """
    if url and url.startswith("//"):
        return "https:" + url
    return url

def determine_product_type(name):
    """
    Determine the product type based on hardcoded keyword matching.
    """
    name_lower = name.lower() if name else ""
    for main_category, subcategories in PRODUCT_CATEGORIES.items():
        for subcategory, keywords in subcategories.items():
            if isinstance(keywords, dict):  # Handle nested subcategories
                for nested_keywords in keywords.values():
                    for keyword in nested_keywords:
                        if keyword in name_lower:
                            return f"{main_category} > {subcategory}"
            else:
                for keyword in keywords:
                    if keyword in name_lower:
                        return f"{main_category} > {subcategory}"
    return "Unknown"


def scrape_product_details(product_url):
    """
    Scrape product details using Selenium for all websites.
    """
    try:
        # Set up Selenium WebDriver
        options = Options()
        options.add_argument("--headless")  # Ensure headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-images")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Open the product URL
        driver.get(product_url)

        # Extract product name
        try:
            # Try multiple potential selectors for product titles
            name_selectors = [
                "h1.product__title",          # unaiclothing example
                "h1.product-single__title",   # Other webshop
                "h1.product-title",           # Another common class
                "h1"                          # General fallback
            ]
            
            name = None
            for selector in name_selectors:
                try:
                    name_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    name = name_element.text.strip()
                    if name:  # If a valid name is found, stop here
                        break
                except Exception:
                    continue  # If current selector fails, try the next one
            
            if not name:
                raise Exception("No product name found.")
        except Exception as e:
            print(f"Error extracting name for {product_url}: {e}")
            name = "Unknown Product"

        # Extract product price
        try:
            # Define a list of possible selectors for the price
            price_selectors = [
                ".price-item--sale.price-item--last",    # Sale price
                "span[data-product-price]",              # Data attribute
                "span.product__price",                  # General product price
                "span.product__price--regular",         # Specific class for regular price
                ".price-item--regular"                  # Another fallback for regular price
            ]

            price_text = None
            for selector in price_selectors:
                try:
                    price_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    price_text = price_element.text.strip()
                    if price_text:  # Stop when valid price is found
                        break
                except Exception:
                    continue  # Try the next selector if current one fails
            
            if not price_text:
                raise Exception("No price found on the page.")
        except Exception as e:
            print(f"Could not find price element for {product_url}: {e}")
            price_text = None

        # Convert price text to a float
        try:
            if price_text:
                price = float(price_text.replace("kr", "").replace("$", "").replace(",", "").replace("USD", "").replace("DKK", "").strip())
            else:
                price = None
        except Exception as e:
            print(f"Error converting price for {product_url}: {e}")
            price = None

        # Extract image URL
        try:
            # Priority 1: Target the specific product image container
            try:
                main_image_element = driver.find_element(By.CSS_SELECTOR, ".product-image-main img[src]")
                image_url = main_image_element.get_attribute("src")
                if image_url.startswith("//"):
                    image_url = "https:" + image_url  # Normalize protocol-relative URL
                print(f"Product image extracted from product-image-main: {image_url}")
            except Exception:
                print("No image found in product-image-main container. Falling back to general search.")
                image_url = None

            # Priority 2: Search through all images if the specific container fails
            if not image_url:
                images = driver.find_elements(By.CSS_SELECTOR, "img[src]")
                for i, image in enumerate(images):
                    image_src = image.get_attribute("src")
                    if not image_src:
                        continue  # Skip if the source is empty

                    # Normalize protocol-relative URL
                    if image_src.startswith("//"):
                        image_src = "https:" + image_src

                    # Skip logos, banners, or irrelevant images
                    if "logo" in image_src.lower() or "banner" in image_src.lower():
                        continue

                    # Check dimensions to exclude small images
                    try:
                        width = int(image.get_attribute("width") or 0)
                        height = int(image.get_attribute("height") or 0)
                        if width < 300 or height < 300:
                            continue  # Skip small images
                    except ValueError:
                        pass  # Skip images without valid dimensions

                    # If we reach here, it's a valid product image
                    image_url = image_src
                    print(f"Fallback image selected: {image_url}")
                    break

            # Priority 3: Check <noscript> if no image found
            if not image_url:
                try:
                    noscript_tag = driver.find_element(By.CSS_SELECTOR, "noscript")
                    soup = BeautifulSoup(noscript_tag.get_attribute("innerHTML"), "html.parser")
                    img_tag = soup.find("img")
                    if img_tag and "src" in img_tag.attrs:
                        image_url = img_tag["src"]
                        if image_url.startswith("//"):
                            image_url = "https:" + image_url  # Normalize protocol-relative URL
                        print(f"Image extracted from <noscript>: {image_url}")
                except Exception:
                    print("No valid image found in <noscript>.")

            # Priority 4: Check Open Graph <meta> tags as the last fallback
            if not image_url:
                try:
                    og_image = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']")
                    image_url = og_image.get_attribute("content")
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url  # Normalize protocol-relative URL
                    print(f"Open Graph image extracted: {image_url}")
                except Exception:
                    print("No Open Graph image found.")

            # If still no image, log the failure
            if not image_url:
                print(f"No valid image found for {product_url}.")

        except Exception as e:
            print(f"Error extracting image URL for {product_url}: {e}")
            image_url = None

        # Extract product type
        try:
            product_type = None

            # Strategy 1: Search for JSON-LD schema.org structured data
            try:
                script_elements = driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
                for script in script_elements:
                    try:
                        structured_data = json.loads(script.get_attribute('innerHTML'))
                        if isinstance(structured_data, list):
                            # If multiple JSON objects exist, iterate through them
                            for obj in structured_data:
                                if obj.get("@type") == "Product" and obj.get("category"):
                                    product_type = obj["category"]
                                    break
                        elif structured_data.get("@type") == "Product" and structured_data.get("category"):
                            product_type = structured_data["category"]
                        if product_type:
                            print(f"Found product type in schema.org: {product_type}")
                            break
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON-LD elements
            except Exception as e:
                print(f"Error extracting schema.org data: {e}")

            # Strategy 2: Validate extracted product type
            if product_type and product_type.lower() in ["clothing", "product"]:
                print(f"Ignoring generic product type: {product_type}")
                product_type = None  # Ignore generic values

            # Strategy 3: Fallback to hardcoded keyword matching
            if not product_type:
                product_type = determine_product_type(name)


            # Log if product type remains unknown
            if product_type == "Unknown":
                print(f"Warning: Product type not found for URL {product_url}")

        except Exception as e:
            print(f"Error extracting product type for {product_url}: {e}")
            product_type = "Unknown"

        # Extract product description
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, "div.product-description, meta[name='description']")
            description = description_element.text.strip() if description_element.tag_name == "div" else description_element.get_attribute("content")
        except Exception as e:
            print(f"Error extracting description for {product_url}: {e}")
            description = None

        driver.quit()

        return {
            "name": name,
            "price": price,
            "image_url": image_url,
            "description": description,
            "type": product_type,
            "product_url": product_url,
        }
    except Exception as e:
        print(f"Error scraping product with Selenium: {product_url}: {e}")
        return None

    
def process_websites_file(file_path):
    """
    Read websites from a file and scrape shop details.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        with open(file_path, "r") as file:
            websites = [line.strip() for line in file if line.strip()]

        for website in websites:
            try:
                print(f"Processing website: {website}")
                shop_details = scrape_shop_details(website)
                if shop_details:
                    save_shop_details(cursor, shop_details)
            except Exception as e:
                print(f"Failed to process website {website}: {e}")

        conn.commit()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing websites file: {e}")
    finally:
        conn.close()

def get_shop_id_from_url(cursor, product_url):
    """
    Get the shop ID for a given product URL by matching the normalized base URL.
    """
    parsed_url = urlparse(product_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}".rstrip('/')

    print(f"Base URL extracted: {base_url}")  # Debugging line

    cursor.execute("""
        SELECT id FROM shops 
        WHERE website_url = ? OR website_url LIKE ?
    """, (base_url, f"%{parsed_url.netloc}%"))
    shop_row = cursor.fetchone()

    return shop_row[0] if shop_row else None

def scrape_shop_details(shop_url):
    """
    Scrape details about a shop based on its homepage URL, including 'About Us' information if available.
    """
    try:
        # Set up Selenium WebDriver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Open the shop's homepage
        driver.get(shop_url)
        time.sleep(2)  # Allow some time for JavaScript to execute

        # Extract shop name
        try:
            shop_name = driver.title.strip()
        except Exception as e:
            print(f"Error extracting shop name for {shop_url}: {e}")
            shop_name = "Unknown Shop"

        driver.quit()

        return {
            "name": shop_name,
            "website_url": shop_url
        }
    except Exception as e:
        print(f"Error scraping shop details: {e}")
        return None

def save_shop_details(cursor, shop_details):
    """
    Save shop details into the `shops` table if not already present.
    """
    try:
        # Check if the shop already exists
        cursor.execute("SELECT id FROM shops WHERE website_url = ?", (shop_details["website_url"],))
        shop_row = cursor.fetchone()

        if shop_row:
            print(f"Shop already exists: {shop_details['website_url']}")
            return shop_row[0]  # Return the existing shop ID

        # Insert the shop into the table
        cursor.execute("""
            INSERT INTO shops (name, website_url)
            VALUES (?, ?)
        """, (shop_details["name"], shop_details["website_url"]))
        shop_id = cursor.lastrowid
        print(f"Saved shop: {shop_details['website_url']}")
        return shop_id
    except sqlite3.IntegrityError as e:
        print(f"Failed to save shop: {e}")
        return None


def scrape_all_products(websites_file):
    """
    Scrape all products and associate them with shops.
    """
    # Step 1: Process websites file
    process_websites_file(websites_file)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Step 2: Fetch unscraped products from the `crawled` table
    # Juster LIMIT til det antal produkter den skal scrape
    cursor.execute("""
        SELECT c.id, c.url
        FROM crawled c
        LEFT JOIN products p ON c.url = p.product_url
        WHERE p.product_url IS NULL  -- Ensures the product hasn't been scraped yet
        ORDER BY RANDOM()
        LIMIT 15
    """)

    crawled_data = cursor.fetchall()

    for crawl_id, product_url in crawled_data:
        print(f"Scraping product: {product_url}")

        # Step 3: Find the corresponding shop ID
        shop_id = get_shop_id_from_url(cursor, product_url)
        if not shop_id:
            print(f"No matching shop for product URL: {product_url}. Skipping...")
            continue

        # Step 4: Scrape product details
        details = scrape_product_details(product_url)

        if details and details["name"] and details["price"] is not None:
            try:
                # Save the product details into the `products` table
                cursor.execute("""
                INSERT INTO products (name, price, description, product_url, image_url, product_type, source_id, shop_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                details["name"], 
                details["price"], 
                details["description"], 
                details["product_url"], 
                details["image_url"], 
                details["type"],  # Use the product_type field extracted earlier
                crawl_id, 
                shop_id
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
        scrape_all_products("websites.txt")
    except KeyboardInterrupt:
        print("Script interrupted. Saving progress...")
