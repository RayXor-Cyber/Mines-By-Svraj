python
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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json  # For JSON parsing
from twocaptcha import TwoCaptcha  # For 2Captcha service (example)
import cv2  # For image processing (optional)
import numpy as np  # For numerical operations
from sklearn.model_selection import train_test_split  # For machine learning
from sklearn.ensemble import RandomForestClassifier  # For machine learning
from sklearn.neighbors import KNeighborsClassifier  # For machine learning
from sklearn.svm import SVC  # For machine learning


# --- Helper Functions ---

def find_element_by_attribute(attribute, attribute_value, element_type):
    """Finds an element by its attribute (ID, class, name) and falls back to XPath/CSS selector."""
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
    except NoSuchElementException:
        return find_element_by_xpath_or_css(attribute_value)

def find_element_by_xpath_or_css(element_identifier):
    """Finds an element using XPath or CSS selector as a fallback."""
    try:
        element = driver.find_element(By.XPATH, element_identifier)
        return element
    except NoSuchElementException:
        try:
            element = driver.find_element(By.CSS_SELECTOR, element_identifier)
            return element
        except NoSuchElementException:
            return None

def wait_for_element(locator, by, timeout=10):
    """Waits for an element to be visible on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, locator))
        )
        return element
    except TimeoutException:
        return None


# --- Game Initialization ---

def initialize_game():
    """Initializes the game by inserting bet amount, number of mines, and clicking start."""
    bet_amount_input = find_element_by_attribute("id", "bet-amount", "ID")  # Replace with actual ID
    if bet_amount_input is None:
        bet_amount_input = find_element_by_attribute("name", "bet-amount", "NAME")
    if bet_amount_input is None:
        raise Exception("Bet amount input field not found.")
    bet_amount_input.clear()  # Clear any previous value
    bet_amount_input.send_keys(bet_amount)  # Use the input bet amount

    num_mines_input = find_element_by_attribute("id", "num-mines", "ID")  # Replace with actual ID
    if num_mines_input is None:
        num_mines_input = find_element_by_attribute("name", "num-mines", "NAME")
    if num_mines_input is None:
        raise Exception("Number of mines input field not found.")
    num_mines_input.clear()  # Clear any previous value
    num_mines_input.send_keys(num_mines)  # Use the input number of mines

    start_game_button = find_element_by_attribute("id", "start-game", "ID")  # Replace with actual ID
    if start_game_button is None:
        start_game_button = find_element_by_attribute("class", "start-game", "CLASS")
    if start_game_button is None:
        raise Exception("Start game button not found.")
    start_game_button.click()


# --- Login Logic ---

def login():
    """Handles the login process."""
    phone_number_field = find_element_by_attribute("name", "phone_number", "NAME")
    if phone_number_field is None:
        phone_number_field = find_element_by_attribute("id", "phone_number", "ID")
    if phone_number_field is None:
        raise Exception("Phone number field not found.")

    password_field = find_element_by_attribute("name", "password", "NAME")
    if password_field is None:
        password_field = find_element_by_attribute("id", "password", "ID")
    if password_field is None:
        raise Exception("Password field not found.")

    select_country("Nigeria")  # Select Nigeria
    phone_number_field.clear()  # Clear any previous value
    phone_number_field.send_keys(phone_number)  # Use the input phone number
    password_field.clear()  # Clear any previous value
    password_field.send_keys(password)  # Use the input password

    login_button = find_element_by_attribute("id", "login-button", "ID")
    if login_button is None:
        login_button = find_element_by_attribute("class", "login-button", "CLASS")
    if login_button is None:
        raise Exception("Login button not found.")

    login_button.click()


# --- Game Logic ---

def select_country(country_name):
    """Selects the specified country in the country dropdown."""
    country_dropdown = find_element_by_attribute("id", "country-dropdown", "ID")  # Replace with actual ID
    if country_dropdown is None:
        country_dropdown = find_element_by_attribute("class", "country-dropdown", "CLASS")
    if country_dropdown is None:
        raise Exception("Country dropdown not found.")

    country_dropdown.click()  # Open the dropdown

    # Find and click the option for the specified country
    for option in country_dropdown.find_elements(By.TAG_NAME, "option"):
        if option.text == country_name:
            option.click()
            return

    raise Exception(f"Country '{country_name}' not found in dropdown.")


def analyze_javascript():
    """Analyzes the game's JavaScript code for mine locations (using BeautifulSoup)."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    script_tags = soup.find_all('script')
    for script in script_tags:
        if "tileData" in script.text:
            js_code = script.text
            # Extract tile data using BeautifulSoup (more robust than regex)
            tile_data_str = re.search(r"var tileData = \[(.*?)\];", js_code).group(1)
            tile_data = [int(tile.split(':')[0]) for tile in tile_data_str.split(',') if 'mine' in tile]
            return tile_data
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
                # Assuming JSON response with a "mines" array
                response_json = json.loads(response_data)
                if "mines" in response_json:
                    self.mine_locations.extend(response_json["mines"])
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


def get_safe_tiles():
    """Gets a list of safe tiles based on mine locations."""
    mine_locations = analyze_network_requests()  # Or analyze_javascript()
    all_tiles = driver.find_elements(By.CLASS_NAME, "game-tile")
    safe_tiles = [tile for i, tile in enumerate(all_tiles) if i not in mine_locations]
    return safe_tiles


def click_tile(tile):
    """Clicks a given tile."""
    tile.click()


def play_game():
    """Plays the game by selecting tiles and cashing out."""
    max_tiles = 10  # Replace with the maximum number of tiles allowed
    tiles_clicked = 0
    clicked_tiles = []  # Keep track of clicked tiles

    while tiles_clicked < max_tiles:
        safetiles = getsafetiles()
        if safetiles:
            # Prioritize tiles near previously clicked safe tiles
            if clickedtiles:
                closesttile = min(safetiles, key=lambda tile: getdistance(tile, clickedtiles[-1]))
                randomtile = closesttile
            else:
                randomtile = random.choice(safetiles)

            clicktile(randomtile)
            tilesclicked += 1
            clickedtiles.append(randomtile)
            time.sleep(0.5)  # Adjust delay as needed
        else:
            print("No safe tiles found, stopping.")
            break

    cashout()
    quitgame()


def cashout():
    """Clicks the cash-out button and displays account balance."""
    cashoutbutton = findelementbyattribute("id", "cashout-button", "ID")
    if cashoutbutton is None:
        cashoutbutton = findelementbyattribute("class", "cashout-button", "CLASS")
    if cashoutbutton is None:
        raise Exception("Cashout button not found.")
    cashoutbutton.click()

    # Display account balance (assuming a balance element exists)
    balanceelement = findelementbyattribute("id", "balance", "ID")  # Replace with actual ID
    if balanceelement is None:
        balanceelement = findelementbyattribute("class", "balance", "CLASS")
    if balanceelement is None:
        print("Account balance not found.")
    else:
        balance = balanceelement.text
        print(f"Account balance: {balance}")

def quitgame():
    """Clicks the quit button."""
    quitbutton = findelementbyattribute("id", "quit-button", "ID")
    if quitbutton is None:
        quitbutton = findelementbyattribute("class", "quit-button", "CLASS")
    if quitbutton is None:
        raise Exception("Quit button not found.")
    quitbutton.click()


# --- Anti-Bot Measures ---

def bypasscaptcha():
    """Handles CAPTCHA challenges using 2Captcha service."""
    try:
        captchaelement = driver.findelement(By.XPATH, "//img@class='captcha-image'")  # Replace with actual XPath
        captchaurl = captchaelement.getattribute('src')
        solver = TwoCaptcha(TWOCAPTCHAAPIKEY)
        result = solver.solveimage(captchaurl)
        captchainput = driver.findelement(By.XPATH, "//input@class='captcha-input'")  # Replace with actual XPath
        captchainput.sendkeys(result'code')
        return True
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return False

def detectandhandleantibot():
    """Detects and handles various anti-bot measures."""
    try:
        # Example: Check for bot detection messages
        botdetectionmessage = driver.findelement(By.XPATH, "//div[@class='bot-detection-message']")  # Replace with actual XPath
        if botdetectionmessage:
            print("Bot detection message detected. Handling...")
            # Implement logic to handle bot detection (e.g., refresh page, use proxy, etc.)
            time.sleep(5)  # Wait for a while and try again
            driver.refresh()
    except NoSuchElementException:
        pass

    # Example: Check for rate limiting
    if driver.title == "Rate Limit Exceeded":
        print("Rate limit exceeded. Handling...")
        # Implement logic to handle rate limiting (e.g., wait, use a different IP, etc.)
        time.sleep(60)  # Wait for 60 seconds and try again

    # Example: Check for unusual page loads/redirects
    if driver.currenturl != GAMEURL:
        print("Unexpected URL change detected. Handling...")
        # Implement logic to handle unexpected redirects (e.g., go back to the game URL)
        driver.get(GAMEURL)


# --- Tile Distance Calculation ---

def getdistance(tile1, tile2):
    """Calculates the distance between two tiles based on tile grid layout."""
    tilesize = 50  # Replace with the actual tile size in pixels
    gridx = tile1.location['x'] // tilesize
    gridy = tile1.location['y'] // tilesize
    grid_x2 = tile2.location['x'] // tile_size
    grid_y2 = tile2.location['y'] // tile_size
    return abs(grid_x - grid_x2) + abs(grid_y - grid_y2)  # Manhattan distance


# --- Machine Learning (Optional) ---

def extract_tile_features(tile):
    """Extracts features from a tile for machine learning."""
    # Assuming tile has a background color and text content
    location = tile.location
    size = tile.size
    color = tile.value_of_css_property("background-color")
    text = tile.text
    return [location['x'], location['y'], size['width'], size['height'], color, text]


def train_mine_detector(tile_data):
    """Trains a machine learning model to predict mine locations."""
    features = []
    labels = []
    for i, tile in enumerate(driver.find_elements(By.CLASS_NAME, "game-tile")):
        features.append(extract_tile_features(tile))
        labels.append(1 if i in tile_data else 0)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # Train different models and evaluate them
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Machine": SVC(kernel='linear', random_state=42)
    }

    best_model = None
    best_accuracy = 0

    for name, model in models.items():
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        print(f"Model: {name}, Accuracy: {accuracy}")
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model

    return best_model



def predict_mine(tile, model):
    """Predicts if a tile contains a mine using the trained model."""
    tile_features = extract_tile_features(tile)
    prediction = model.predict([tile_features])
    return prediction[0]


# --- Main Execution ---

def main():
    """Main function to execute the script."""
    global phone_number, password, bet_amount, num_mines
    phone_number = input("Enter your phone number: ")
    while True:
        if phone_number.isdigit() and len(phone_number) == 11:
            break
        else:
            print("Invalid phone number. Please enter a valid 11-digit number.")
            phone_number = input("Enter your phone number: ")

    password = input("Enter your password: ")
    while True:
        if len(password) >= 6:
            break
        else:
            print("Invalid password. Please enter a password with at least 6 characters.")
            password = input("Enter your password: ")

    bet_amount = input("Enter bet amount: ")
    while True:
        try:
            bet_amount = int(bet_amount)
            if bet_amount > 0:
                break
            else:
                print("Invalid bet amount. Please enter a positive number.")
        except ValueError:
            print("Invalid bet amount. Please enter a number.")
        bet_amount = input("Enter bet amount: ")

    num_mines = input("Enter number of mines: ")
    while True:
        try:
            num_mines = int(num_mines)
            if num_mines > 0:
                break
            else:
                print("Invalid number of mines. Please enter a positive number.")
        except ValueError:
            print("Invalid number of mines. Please enter a number.")
        num_mines = input("Enter number of mines: ")

    try:
        # Open the game URL
        driver.get(GAME_URL)

        # Select "Popular" category (automatically detect category)
        popular_category = find_element_by_attribute("id", "popular-category", "ID")  # Replace with actual ID
        if popular_category is None:
            popular_category = find_element_by_attribute("class", "popular-category", "CLASS")
        if popular_category is None:
            raise Exception("Popular category not found.")
        popular_category.click()

        # Select "Mines" game (automatically detect game)
        mines_game = find_element_by_attribute("id", "mines-game", "ID")  # Replace with actual ID
        if mines_game is None:
            mines_game = find_element_by_attribute("class", "mines-game", "CLASS")
        if mines_game is None:
            raise Exception("Mines game not found.")
        mines_game.click()

        # Now proceed with the login process
        login()

        wait_for_element("game-tile", By.CLASS_NAME)
        initialize_game()  # Initialize game settings
        tile_data = analyze_javascript()  # Get initial mine data
        model = train_mine_detector(tile_data)  # Train the model
        play_game(model)

        # Ask before quitting
        quit_choice = input("Do you want to quit the browser? (y/n): ")
        if quit_choice.lower() == 'y':
            driver.quit()
    except Exception as e:
        print(f"An error occurred: {e}")
        detect_and_handle_anti_bot()  # Handle anti-bot measures if an error occurs
    finally:
        driver.quit()


def play_game(model):
    """Plays the game by selecting tiles and cashing out."""
    max_tiles = 10  # Replace with the maximum number of tiles allowed
    tiles_clicked = 0
    clicked_tiles = []  # Keep track of clicked tiles

    while tiles_clicked < max_tiles:
        safe_tiles = get_safe_tiles()
        if safe_tiles:
            # Prioritize tiles near previously clicked safe tiles
            if clicked_tiles:
                closest_tile = min(safe_tiles, key=lambda tile: get_distance(tile, clicked_tiles[-1]))
                random_tile = closest_tile
            else:
                random_tile = random.choice(safe_tiles)

            # Predict if the tile is a mine
            is_mine = predict_mine(random_tile, model)

            if is_mine == 0:  # If prediction is not a mine
                click_tile(random_tile)
                tiles_clicked += 1
                clicked_tiles.append(random_tile)
                time.sleep(0.5)  # Adjust delay as needed
            else:
                print("Predicted mine, skipping...")
        else:
            print("No safe tiles found, stopping.")
            break

    cash_out()
    quit_game()


if __name__ == "__main__":
    main()


