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
        options.add_argument("--headless")  # Ensure headless mode
        options.add_argument("--disable-gpu")  # Disable GPU acceleration (important for headless mode)
        options.add_argument("--no-sandbox")  # Avoid issues in certain environments
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
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            name = name_element.text.strip()
        except Exception as e:
            print(f"Error extracting name for {product_url}: {e}")
            name = "Unknown Product"

        # Extract product price
        try:
            try:
                sale_price_element = driver.find_element(By.CSS_SELECTOR, ".price-item--sale.price-item--last")
                price_text = sale_price_element.text.strip()
            except Exception:
                print("No sale price found. Falling back to regular price.")

            # Try the first selector
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-product-price], span.product__price"))
            )
            price_text = price_element.text.strip()
        except Exception:
            try:
                # Fallback to another common selector
                price_element = driver.find_element(By.CSS_SELECTOR, ".price-item--regular")
                price_text = price_element.text.strip()
            except Exception:
                print(f"Could not find price element for {product_url}")
                price_text = None

        # Convert price text to a float
        try:
            price = float(price_text.replace("kr", "").replace("$", "").replace(",", "").replace("USD", "").replace("DKK", "").strip())
        except Exception as e:
            print(f"Error converting price for {product_url}: {e}")
            price = None


            # Extract product name
            try:
                name = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                name = "Unknown Product"
                
        # Extract image URL
        try:
            images = driver.find_elements(By.CSS_SELECTOR, "img[src]")  # Get all visible images
            image_url = None

            # Iterate over images and apply stricter filtering
            for i, image in enumerate(images):
                image_src = image.get_attribute("src")
                if not image_src:
                    continue  # Skip if the source is empty

                # Skip the first image or images containing "logo" or similar patterns
                if i == 0 or "logo" in image_src.lower() or "banner" in image_src.lower():
                    continue

                # Check dimensions or attributes to filter product images
                try:
                    width = int(image.get_attribute("width") or 0)
                    height = int(image.get_attribute("height") or 0)

                    # Skip images that are too small to be product images
                    if width < 300 or height < 300:
                        continue
                except ValueError:
                    pass  # Ignore images without valid dimensions

                # If we reach here, assume it's a valid product image
                image_url = image_src
                break

            # Fallback to <noscript> or Open Graph if no valid image found
            if not image_url:
                try:
                    noscript_tag = driver.find_element(By.CSS_SELECTOR, "noscript")
                    soup = BeautifulSoup(noscript_tag.get_attribute("innerHTML"), "html.parser")
                    img_tag = soup.find("img")
                    if img_tag and "src" in img_tag.attrs:
                        image_url = img_tag["src"]
                except Exception:
                    print(f"No valid image found in <noscript> for {product_url}.")

            if not image_url:
                try:
                    og_image = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']")
                    image_url = og_image.get_attribute("content")
                except Exception:
                    print(f"No Open Graph image found for {product_url}.")

            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

            if not image_url:
                print(f"No valid image found for {product_url}.")
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
    Get the shop ID for a given product URL by matching the base URL.
    """
    parsed_url = urlparse(product_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    cursor.execute("SELECT id FROM shops WHERE website_url = ?", (base_url,))
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

        # Extract "About Us" description
        description = None
        try:
            # Look for "About Us" link in the footer or navigation
            about_link = driver.find_element(By.PARTIAL_LINK_TEXT, "About")
            about_url = about_link.get_attribute("href")

            if about_url:
                print(f"Found 'About Us' page at {about_url}. Scraping content...")
                driver.get(about_url)
                time.sleep(2)

                # Extract main content from the 'About Us' page
                try:
                    about_us_element = driver.find_element(By.TAG_NAME, "body")
                    description = about_us_element.text.strip()
                except Exception as e:
                    print(f"Error extracting About Us content for {about_url}: {e}")
            else:
                description = None
        except Exception as e:
            print(f"No 'About Us' link found for {shop_url}: {e}")

        # If no 'About Us' page, fallback to homepage description (meta description)
        if not description:
            try:
                meta_description = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
                description = meta_description.get_attribute("content")
            except Exception as e:
                print(f"Error extracting meta description for {shop_url}: {e}")
                description = ""

        driver.quit()

        return {
            "name": shop_name,
            "website_url": shop_url,
            "description": description,
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
            INSERT INTO shops (name, website_url, description)
            VALUES (?, ?, ?)
        """, (shop_details["name"], shop_details["website_url"], shop_details["description"]))
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
    cursor.execute("""
        SELECT c.id, c.url
        FROM crawled c
        LEFT JOIN products p ON c.url = p.product_url
        WHERE c.status = 'pending' AND p.product_url IS NULL
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
                    INSERT INTO products (name, price, image_url, description, delivery_options, product_url, source_id, shop_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    details["name"], 
                    details["price"], 
                    details["image_url"], 
                    details["description"], 
                    details["delivery_options"], 
                    details["product_url"], 
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
