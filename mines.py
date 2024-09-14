from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import re

# Initialize the web driver
driver = webdriver.Chrome()  # Or Firefox, Edge, etc.

# Navigate to the game URL
driver.get("https://www.sportybet.com/ng/sportygames/hub88-games/tbg_mines")

# Access Developer Tools
dev_tools = driver.execute_script("return window.devTools")
network_requests = dev_tools.Network.getNetworkRequests()

# Check if already logged in
try:
    # Look for an element that indicates login status 
    logged_in_indicator = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'username') or contains(@class, 'user-name') or contains(text(), 'Profile')] | //img[contains(@class, 'profile-icon') or contains(@class, 'user-avatar')] | //button[contains(text(), 'Logout')]")))  # Adjust XPath as needed
    print("User is already logged in.")
    # Proceed with other activities 
    # ... (Rest of the code for game logic) ...

except TimeoutException:
    # If logged-in indicator not found, proceed with login
    print("User is not logged in. Proceeding with login.")

    # Find login button
    try:
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")))
        login_button.click()
    except:
        print("Login button not found.")

    # ... (Login code) ...

# Wait for the login form elements to be visible
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

try:
    # Detect phone number field
    phone_number_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='tel' or @type='number' or contains(@placeholder, 'Phone') or contains(@placeholder, 'Number')]")))
    phone_number_id = phone_number_field.get_attribute("id")

    # Detect password field
    password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password' or contains(@placeholder, 'Password')]")))
    password_id = password_field.get_attribute("id")

    # Detect login button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    
    except TimeoutException:
    print("Timeout: Login elements not found within the specified time.")
except NoSuchElementException:
    print("Error: One or more login elements were not found on the page.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

    # Prompt for phone number and password
    phone_number = input("Enter your phone number: ")
    password = input("Enter your password: ")


    # Detect country code selection (if present)
    try:
        # Find all select elements near the phone number field
        select_elements = driver.find_elements(By.XPATH, "//input[@id='" + phone_number_id + "']/following-sibling::select")

        if select_elements:
            country_code_select = select_elements[0]  # Assume the first select element is the country code
            country_code_select.click()

            # Find all option elements within the select
            option_elements = country_code_select.find_elements(By.TAG_NAME, "option")

            # Find the Nigeria option
            for option in option_elements:
                if "+234" in option.text:
                    nigeria_option = option
                    nigeria_option.click()
                    break
        else:
            print("Country code selection not found.")

    except Exception as e:
        print(f"Error detecting country code: {e}")


    # Login
    driver.find_element(By.ID, phone_number_id).send_keys(phone_number)
    driver.find_element(By.ID, password_id).send_keys(password)
    login_button.click()

    # Extract game data (example)
    game_state = driver.find_element(By.ID, "game-state").text

    # ... (Implement game logic and action execution) 

# Get user account balance
try:
    balance_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'balance') or contains(@class, 'account-balance') or contains(@class, 'funds') or contains(@class, 'credit') or contains(text(), 'Balance') or contains(text(), 'Credits')]")))  # Adjust XPath as needed
    account_balance = balance_element.text
except:
    account_balance = "Balance not found"

# Prompt for bet amount and number of mines, displaying balance
while True:
    print(f"Your current balance is: {account_balance}")
    bet_amount = input("Enter your bet amount: ")
while True:
    num_mines_str = input("Select number of mines (3, 5, 10, or 20): ")
    if num_mines_str in ["3", "5", "10", "20"]:
        num_mines = int(num_mines_str)
        break
    else:
        print("Invalid input. Please enter 3, 5, 10, or 20.")


# Find and set bet amount
bet_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='number' and (contains(@placeholder, 'Bet') or contains(@placeholder, 'Stake') or contains(@aria-label, 'Bet'))]")))  # Adjust XPath as needed
bet_input.clear()
bet_input.send_keys(bet_amount)

# Find and set number of mines
num_mines_select = wait.until(EC.visibility_of_element_located((By.XPATH, "//select[contains(@name, 'mines') or contains(@class, 'mines-select') or contains(@aria-label, 'Mines')]")))  # Adjust XPath as needed
num_mines_select.click()
num_mines_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[contains(text(), '{num_mines}')]")))  # Adjust XPath as needed
num_mines_option.click()

# Find and click the start game button
start_game_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game') or contains(text(), 'Play') or contains(text(), 'Begin')]")))  # Adjust XPath as needed
start_game_button.click()

# ... (Rest of the code for bomb detection, tile selection, etc.) ...

# Access the Sources tab in the developer tools
sources_tab = dev_tools.Sources.getSourcesTab()

# Iterate through the loaded JavaScript files
for script_file in sources_tab.getScriptFiles():
    script_content = script_file.getContent()

    # Search for patterns related to bomb locations
    def find_bomb_pattern(script_content):
    potential_patterns = [
        r"bomb_locations|tile_data|game_grid",
        r"mines|explosives|danger_tiles",
        r"hidden_tiles|revealed_tiles",
        # Add more potential patterns as needed
    ]

    for pattern in potential_patterns:
        if re.search(pattern, script_content):
            return pattern
    return None

# ... (Rest of the code) ...

bomb_pattern = find_bomb_pattern(script_content)
if bomb_pattern:
    # ... (Proceed with bomb location extraction) ...

# Iterate through network requests
for request in network_requests:
    if "tile" in request.url or "game" in request.url:
        request_data = request.getContent()

        # Extract bomb locations from the request data
        def extract_bomb_locations_from_js(script_content, bomb_pattern):
    # Try different extraction methods based on potential data structures
    try:
        # Attempt to extract from an array
        bomb_locations = re.findall(rf"{bomb_pattern} = \[(.*?)\]", script_content)[0].split(",")
        return bomb_locations
    except:
        pass

    try:
        # Attempt to extract from an object
        bomb_locations = re.findall(rf"{bomb_pattern} = (\{.*?\})", script_content)[0]
        # ... (Parse the object and extract bomb locations) ...
        return bomb_locations
    except:
        pass

    # ... (Add more extraction methods for other data structures) ...

    return None

# ... (Rest of the code) ...

bomb_locations = extract_bomb_locations_from_js(script_content, bomb_pattern)
if bomb_locations:
    # ... (Proceed with tile selection) ...


def play_game():
    tiles = get_game_tiles()  # Initialize tile data (index, selected, etc.)
    bomb_locations = get_bomb_locations()  # Function to extract bomb locations
    selected_count = 0
    while selected_count < 5:
        # Select a random tile that hasn't been selected and doesn't contain a bomb
        tile_index = random.choice([tile["index"] for tile in tiles if not tile["is_selected"] and tile["index"] not in bomb_locations])

        # Select the tile (no need to analyze outcome since we know it's not a bomb)
        select_tile(tile_index)

        tiles[tile_index]["is_selected"] = True
        selected_count += 1

    # ... (Check game state (win/lose) if the game provides a clear win/lose indicator) ...


    # After selecting the maximum number of tiles
if selected_count == 5:
    # Find and click the cash out button
    try:
        cash_out_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Cash Out') or contains(text(), 'Collect') or contains(text(), 'Withdraw') or contains(text(), 'Redeem') or contains(text(), 'Claim')]")))  # Adjust XPath as needed
        cash_out_button.click()

         # Get new account balance
        try:
            balance_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'balance') or contains(@class, 'account-balance') or contains(@class, 'funds') or contains(@class, 'credit') or contains(text(), 'Balance') or contains(text(), 'Credits')]")))  # Adjust XPath as needed
            new_account_balance = balance_element.text
            print(f"Your new balance is: {new_account_balance}")
        except:
            new_account_balance = "New balance not found"

        # Prompt to quit the program
        input("Press Enter to quit the program.")

    except Exception as e:
        print(f"Error during cash out or balance retrieval: {e}")

finally:
    driver.quit() 
