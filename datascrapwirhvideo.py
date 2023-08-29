import time
import os
import pyautogui
import subprocess
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
search_box = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'twotabsearchtextbox')))
search_box.send_keys('laptop')
search_box.submit()

# Rest of the code...
data = []
screenshots_folder = 'screenshots'
os.makedirs(screenshots_folder, exist_ok=True)

# Start screen recording using ffmpeg
output_file = 'screen_record.mp4'
recording_command = ['ffmpeg', '-f', 'gdigrab', '-framerate', '10', '-video_size', '1920x1080', '-i', 'desktop', output_file]
recording_process = subprocess.Popen(recording_command)

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
            product_description = "N/A"
            brand = "N/A"
            model_name = "N/A"
            screen_size = "N/A"
            color = "N/A"
            cpu_model = "N/A"
            ram_memory = "N/A"

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

        # Capture screenshot
        screenshot_path = os.path.join(screenshots_folder, f'{len(data)}.png')
        pyautogui.screenshot(screenshot_path)

    # Check if there is a next page
    next_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.s-pagination-container .s-pagination-next')))
    if 's-pagination-disabled' in next_button.get_attribute('class'):
        break

    # Go to the next page
    next_button.click()

# Stop screen recording
recording_process.terminate()

# Convert screenshots to a video using ffmpeg
ffmpeg_command = ['ffmpeg', '-framerate', '10', '-i', f'{screenshots_folder}/%d.png', '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p', output_file]
subprocess.run(ffmpeg_command, check=True)

# Store the data in a CSV file
df = pd.DataFrame(data)
df.to_csv('amazon_data.csv', index=False)

# Clean up screenshots folder
for file_name in os.listdir(screenshots_folder):
    file_path = os.path.join(screenshots_folder, file_name)
    os.remove(file_path)
os.rmdir(screenshots_folder)

# Clean up
driver.quit()
