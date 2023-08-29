from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import webdriver_manager.chrome
import pandas as pd

# Set up the Selenium WebDriver
driver = webdriver.Chrome(webdriver_manager.chrome.ChromeDriverManager().install())

# Navigate to the Amazon website
driver.get('https://www.amazon.com/')
driver.maximize_window()

# Enter search query and perform search
search_box = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'twotabsearchtextbox')))
search_box.send_keys('laptop')
search_box.submit()


# Rest of the code...
data = []
while True:
    # Wait for search results to load
    search_results = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))

    for result in search_results:
        try:
            product_name = result.find_element(By.CLASS_NAME, 'a-size-mini').text
        except:
            product_name = "N/A"
        try:
            product_description = result.find_element(By.CSS_SELECTOR, '.a-size-base-plus.a-color-base.a-text-normal').text
        except:
            product_description = "N/A"
        try:
            product_price_element = result.find_element(By.CSS_SELECTOR, '.a-price-whole')
            product_price = product_price_element.text
        except:
            product_price = "N/A"
        try:
            product_rating = driver.find_element(By.CSS_SELECTOR, '.a-icon-star-small .a-icon-alt').get_attribute('innerHTML')
        except:
            product_rating = "N/A"
        try:
            product_image = result.find_element(By.CSS_SELECTOR, '.s-image').get_attribute('src')
        except:
            product_image = "N/A"
        try:
            product_category = result.find_element(By.CSS_SELECTOR, '.a-color-secondary .a-size-base.a-link-normal').text
        except:
            product_category = "N/A"

        data.append({
            'Product Name': product_name,
            'Description': product_description,
            'Price': product_price,
            'Rating': product_rating,
            'Image': product_image,
            'Category': product_category
        })

    # Check if there is a next page
    next_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.s-pagination-container .s-pagination-next')))
    if 's-pagination-disabled' in next_button.get_attribute('class'):
        break

    # Go to the next page
    next_button.click()

# Store the data in a CSV file
df = pd.DataFrame(data)
df.to_csv('amazon_data.csv', index=False)

# Clean up
driver.quit()