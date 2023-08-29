import time
import os
import pyautogui
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

# Define screen recording parameters
output_folder = 'screen_record'
os.makedirs(output_folder, exist_ok=True)
screenshot_interval = 0.5  # Interval between consecutive screenshots (in seconds)

# Enter search query and perform search
search_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'twotabsearchtextbox')))
search_box.send_keys('laptop')
search_box.submit()

# Rest of the code...
data = []
while True:
    # Wait for search results to load
    search_results = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))

    for result in search_results:
        try:
            product_title_element = result.find_element(By.CSS_SELECTOR, 'h2 a')
            product_title = product_title_element.text

            # Open the product link in a new tab
            driver.execute_script("window.open(arguments[0]);", product_title_element.get_attribute("href"))
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for the product details page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'feature-bullets')))

            # Extract the description
            try:
                product_description = driver.find_element(By.ID, 'productDescription').text
            except:
                product_description = "N/A"

            # Extract the additional details
            try:
                brand = driver.find_element(By.XPATH, '//th[contains(text(), "Brand")]/following-sibling::td').text
            except:
                brand = "N/A"

            try:
                model_name = driver.find_element(By.XPATH, '//*[@id="poExpander"]/div[1]/div/table/tbody/tr[2]/td[2]/span').text
            except:
                model_name = "N/A"

            try:
                screen_size = driver.find_element(By.XPATH, '//*[@id="poExpander"]/div[1]/div/table/tbody/tr[3]/td[2]/span').text
            except:
                screen_size = "N/A"

            try:
                color = driver.find_element(By.XPATH, '//th[contains(text(), "Color")]/following-sibling::td').text
            except:
                color = "N/A"

            try:
                cpu_model = driver.find_element(By.XPATH, '//*[@id="poExpander"]/div[1]/div/table/tbody/tr[5]/td[2]/span').text
            except:
                cpu_model = "N/A"

            try:
                ram_memory = driver.find_element(By.XPATH, '//*[@id="poExpander"]/div[1]/div/table/tbody/tr[6]/td[2]/span').text
            except:
                ram_memory = "N/A"

            # Switch back to the search results page
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            product_title = "N/A"

        try:
            product_price_element = result.find_element(By.CSS_SELECTOR, '.a-price-whole')
            product_price = product_price_element.text
        except:
            product_price = "N/A"
        try:
            product_rating = result.find_element(By.CSS_SELECTOR, '.a-icon-star-small .a-icon-alt').get_attribute(
                'innerHTML')
        except:
            product_rating = "N/A"
        try:
            product_image = result.find_element(By.CSS_SELECTOR, '.s-image').get_attribute('src')
        except:
            product_image = "N/A"

        data.append({
            'Name': product_title,
            'Description': product_description,
            'Price': product_price,
            'Rating': product_rating,
            'Images': product_image,
            'Brand': brand,
            'Model Name': model_name,
            'Screen Size': screen_size,
            'Color': color,
            'CPU Model': cpu_model,
            'Ram Memory Installed Size': ram_memory
        })

        # Check if there is a next page
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.s-pagination-container .s-pagination-next')))
        if 's-pagination-disabled' in next_button.get_attribute('class'):
            break

        # Go to the next page
        next_button.click()

    # Store the data in a CSV file
    df = pd.DataFrame(data)
    df.to_csv('amazon_data.csv', index=False)

    # Capture screenshots for screen recording
    screenshots_folder = os.path.join(output_folder, f'results_{len(data)}')
    os.makedirs(screenshots_folder, exist_ok=True)
    for i, result in enumerate(search_results):
        result.screenshot(os.path.join(screenshots_folder, f'result_{i}.png'))

    # Wait for the specified interval before capturing the next set of screenshots
    time.sleep(screenshot_interval)

    # Check if there is a next page for recording
    if 's-pagination-disabled' in next_button.get_attribute('class'):
        break

# Clean up
driver.quit()
