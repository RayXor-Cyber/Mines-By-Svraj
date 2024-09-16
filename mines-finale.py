from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
from bs4 import BeautifulSoup
import re
from mitmproxy import http
from mitmproxy.tools.dump import DumpMaster

# Replace with your actual credentials
PHONE_NUMBER = "your_phone_number"
PASSWORD = "your_password"

# Game URL
GAME_URL = "your_game_url"

# Initialize Selenium WebDriver
driver = webdriver.Chrome()  # Or other browser driver
driver.get(GAME_URL)


# Function to automatically detect and select Nigerian Code (Conceptual)
def select_nigerian_code():
    country_code_select = driver.find_element(By.XPATH, "//select[@name='country_code']")  # Adjust XPATH if needed
    if country_code_select is None:
        country_code_select = driver.find_element(By.XPATH, "//select[@id='country_code']")
    if country_code_select is None:
        print("Country code select element not found.")
        exit()
    
    code_elements = country_code_select.find_elements(By.TAG_NAME, "option")
    for code in code_elements:
        if code.text == "+234":  # Check if the country code is Nigeria
            code.click()
            return
    print("Nigerian code not found.")

# Function to find element by attribute (ID, Class, etc.)
def find_element_by_attribute(attribute, attribute_value, element_type):
    try:
        if element_type == "ID":
            element = driver.find_element(By.ID, attribute_value)
        elif element_type == "CLASS":
            element = driver.find_element(By.CLASS_NAME, attribute_value)
        elif element_type == "NAME":
            element = driver.find_element(By.NAME, attribute_value)
        else:
            return None
        return element
    except:
        return find_element_by_xpath_or_css(attribute_value)


# Function to find element by xpath or css selector
def find_element_by_xpath_or_css(element_identifier):
    try:
        # Try finding by XPath first
        element = driver.find_element(By.XPATH, element_identifier)
        return element
    except:
        try:
            # If XPath fails, try finding by CSS selector
            element = driver.find_element(By.CSS_SELECTOR, element_identifier)
            return element
        except:
            return None


# Login
phone_number_field = find_element_by_attribute("name", "phone_number", "NAME") # Replace with actual ID
if phone_number_field is None:
    phone_number_field = find_element_by_attribute("id", "phone_number", "ID") # Replace with actual ID
if phone_number_field is None:
    print("Phone number field not found.")
    exit()

password_field = find_element_by_attribute("name", "password", "NAME") # Replace with actual ID
if password_field is None:
    password_field = find_element_by_attribute("id", "password", "ID") # Replace with actual ID
if password_field is None:
    print("Password field not found.")
    exit()

select_nigerian_code()  # Call the function to select the code
phone_number_field.send_keys(PHONE_NUMBER)
password_field.send_keys(PASSWORD)

login_button = find_element_by_attribute("id", "login-button", "ID") # Replace with actual ID
if login_button is None:
    login_button = find_element_by_attribute("class", "login-button", "CLASS") # Replace with actual ID
if login_button is None:
    print("Login button not found.")
    exit()

login_button.click()


# Wait for game to load
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "game-tile")))  # Replace with actual class name


# Function to analyze JavaScript for mine locations (Conceptual)
def analyze_javascript():
    page_source = driver.page_source
    js_code = re.findall(r'<script>(.*?)</script>', page_source, re.DOTALL)
    # Extract tile data from JavaScript code (Example)
    tile_data = re.findall(r"var tileData = \[(.*?)\];", str(js_code), re.DOTALL)
    if tile_data:
        mine_locations = []
        for tile in tile_data[0].split(','):
            if 'mine' in tile:
                mine_locations.append(int(tile.split(':')[0]))
        return mine_locations
    else:
        return []

# Class to capture and analyze network requests
class NetworkAnalyzer:
    def __init__(self):
        self.mine_locations = []

    def request(self, flow: http.HTTPFlow):
        if "tile_data" in flow.request.url:  # Adjust URL pattern if needed
            try:
                response_data = flow.response.text
                # Extract mine locations from response data (Example)
                mine_indices = re.findall(r'"mine":(\d+)', response_data)
                self.mine_locations.extend(map(int, mine_indices))
            except:
                pass

    def get_mine_locations(self):
        return self.mine_locations

# Function to analyze network requests
def analyze_network_requests():
    analyzer = NetworkAnalyzer()
    master = DumpMaster(analyzer)
    master.run()
    return analyzer.get_mine_locations()


# Function to get a list of safe tiles
def get_safe_tiles():
    mine_locations = analyze_network_requests()  # Or analyze_javascript()
    all_tiles = driver.find_elements(By.CLASS_NAME, "game-tile")  # Replace with actual class name
    safe_tiles = []
    for i, tile in enumerate(all_tiles):
        if i not in mine_locations:
            safe_tiles.append(tile)
    return safe_tiles


# Function to click a tile
def click_tile(tile):
    tile.click()


# Main Game Loop
max_tiles = 10  # Replace with the maximum number of tiles allowed
tiles_clicked = 0
while tiles_clicked < max_tiles:
    safe_tiles = get_safe_tiles()
    if safe_tiles:
        random_tile = random.choice(safe_tiles)
        click_tile(random_tile)
        tiles_clicked += 1
        time.sleep(0.5)  # Adjust delay as needed
    else:
        print("No safe tiles found, stopping.")
        break

# Cash Out
cashout_button = find_element_by_attribute("id", "cashout-button", "ID") # Replace with actual ID
if cashout_button is None:
    cashout_button = find_element_by_attribute("class", "cashout-button", "CLASS") # Replace with actual ID
if cashout_button is None:
    print("Cashout button not found.")
    exit()
cashout_button.click()

# Quit (if applicable)
quit_button = find_element_by_attribute("id", "quit-button", "ID") # Replace with actual ID
if quit_button is None:
    quit_button = find_element_by_attribute("class", "quit-button", "CLASS") # Replace with actual ID
if quit_button is None:
    print("Quit button not found.")
    exit()
quit_button.click()

# Close the browser
driver.quit()
