from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from database import insert_watch, check_watch_exists, update_watch, test_watch_data

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def parse_page(url, conn):
    driver = setup_driver()
    new_items_count = 0
    updated_items_count = 0
    total_items_count = 0

    try:
        print(f"Processing page: {url}")
        driver.get(url)
        
        links = driver.find_elements(By.CSS_SELECTOR, 'a.js-article-item.article-item.block-item.rcard')
        
        for link in links:
            href = link.get_attribute('href')
            print(f"Processing link: {href}")
            
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(href)
            
            try:
                script_tag = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'script[type="application/ld+json"]'))
                )
                json_data = json.loads(script_tag.get_attribute('innerHTML'))
                
                breadcrumb_list = next((item for item in json_data['@graph'] if item['@type'] == 'BreadcrumbList'), None)
                product_data = next((item for item in json_data['@graph'] if item['@type'] == 'Product'), None)
                
                if breadcrumb_list and product_data:
                    product_id = product_data.get('productID', 'N/A')
                    
                    brand = product_data.get('brand', 'N/A')
                    model = next((item['item']['name'] for item in breadcrumb_list['itemListElement'] 
                                  if item['position'] == 3), 'N/A').replace(' watches', '')
                    ref = product_data.get('sku', 'N/A')
                    price = product_data.get('offers', {}).get('price', 'N/A')
                    currency = product_data.get('offers', {}).get('priceCurrency', 'N/A')
                    year = product_data.get('productionDate', 'N/A')
                    
                    condition = 'N/A'
                    try:
                        condition_element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button.link.js-conditions"))
                        )
                        condition = condition_element.text.strip()
                    except TimeoutException:
                        print(f"Timeout waiting for condition button on {href}")
                        try:
                            condition_element = driver.find_element(By.CSS_SELECTOR, ".article-condition span")
                            condition = condition_element.text.strip()
                        except NoSuchElementException:
                            print(f"Could not find condition element on {href}")
                    
                    watch_data = [product_id, brand, model, ref, price, currency, condition, year]
                    
                    if check_watch_exists(conn, product_id):
                        update_watch(conn, watch_data)
                        updated_items_count += 1
                        print(f"Updated existing watch: {product_id}")
                    else:
                        insert_watch(conn, watch_data)
                        new_items_count += 1
                        print(f"Added new watch: {product_id}")
                    
                    total_items_count += 1
            
            except Exception as e:
                print(f"Error processing {href}: {str(e)}")
            
            finally:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
    
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    
    finally:
        driver.quit()

    return new_items_count, updated_items_count, total_items_count

def scrape_brand(brand, conn, url, max_pages=10):
    total_new_items = 0
    total_updated_items = 0
    total_items = 0

    for page in range(1, max_pages + 1):
        page_url = f"{url}?page={page}"
        new_items, updated_items, items = parse_page(page_url, conn)
        total_new_items += new_items
        total_updated_items += updated_items
        total_items += items

        print(f"Page {page} complete. New: {new_items}, Updated: {updated_items}, Total: {items}")

    return total_new_items, total_updated_items, total_items

def test_first_watch(url):
    driver = setup_driver()
    try:
        print(f"Accessing page: {url}")
        driver.get(url)
        
        # Find the first watch link
        first_watch_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.js-article-item.article-item.block-item.rcard'))
        )
        href = first_watch_link.get_attribute('href')
        print(f"Found first watch link: {href}")
        
        # Navigate to the first watch page
        driver.get(href)
        
        # Extract data
        script_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'script[type="application/ld+json"]'))
        )
        json_data = json.loads(script_tag.get_attribute('innerHTML'))
        
        breadcrumb_list = next((item for item in json_data['@graph'] if item['@type'] == 'BreadcrumbList'), None)
        product_data = next((item for item in json_data['@graph'] if item['@type'] == 'Product'), None)
        
        if breadcrumb_list and product_data:
            product_id = product_data.get('productID', 'N/A')
            brand = product_data.get('brand', 'N/A')
            model = next((item['item']['name'] for item in breadcrumb_list['itemListElement'] 
                          if item['position'] == 3), 'N/A').replace(' watches', '')
            ref = product_data.get('sku', 'N/A')
            price = product_data.get('offers', {}).get('price', 'N/A')
            currency = product_data.get('offers', {}).get('priceCurrency', 'N/A')
            year = product_data.get('productionDate', 'N/A')
            
            condition = 'N/A'
            try:
                condition_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.link.js-conditions"))
                )
                condition = condition_element.text.strip()
            except TimeoutException:
                print("Timeout waiting for condition button")
                try:
                    condition_element = driver.find_element(By.CSS_SELECTOR, ".article-condition span")
                    condition = condition_element.text.strip()
                except NoSuchElementException:
                    print("Could not find condition element")
            
            watch_data = [product_id, brand, model, ref, price, currency, condition, year]
            test_watch_data(watch_data)
        else:
            print("Could not extract watch data from JSON-LD")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        driver.quit()