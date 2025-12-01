import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# --- CONFIGURATION ---
BASE_URL = "https://shop.amul.com/en/" # Home Page URL
ITEM_URL = "https://shop.amul.com/en/product/amul-high-protein-rose-lassi-200-ml-or-pack-of-30" # Enter the product page URL here
NTFY_TOPIC = "divyenegi-stock-alert" # Change this to your preferred unique ntfy.sh topic
ADDRESS_STRING="500089" # Enter such string such that the first result is the required one (For Amul, pincode works best)
CHECK_INTERVAL_MIN = 5
CHECK_INTERVAL_MAX = 20

def get_config():
    global ITEM_URL, NTFY_TOPIC, ADDRESS_STRING

    ITEM_URL = input("Enter Product URL (shop.amul.com): ").strip() or ITEM_URL
    NTFY_TOPIC = input("Enter your unique ntfy.sh Topic: ").strip() or NTFY_TOPIC
    ADDRESS_STRING = input("Enter such string such that the first result is the required one (For Amul, pincode works best): ").strip() or ADDRESS_STRING

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Overwrite the permissions API to look real
            const originalQuery = window.navigator.permissions.query;
            return window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """
    })
    return driver

def inject_and_validate_location(driver):
    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n>> [Attempt {attempt+1}/{max_retries}] Setting Location...")
        
        try:
            driver.get(f"{BASE_URL}")
            time.sleep(5)
            
            print(f">> Entering Address: {ADDRESS_STRING}...")
            locationPopup = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='search']"))
            )
            locationPopup.send_keys(f"{ADDRESS_STRING}")
            time.sleep(3)
            
            print(">> Clicking first address result...")
            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'searchitem-name')][1]"))
            )
            first_result.click()
            time.sleep(5)

            print(">> Validating Location...")
            location_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'loc_area')]"))
            )
            
            location_text = location_element.text.lower()
            print(f">> Detected Location Text: '{location_text}'")

            if "Select Pincodes" in location_text:
                print(">> FAILURE: Location not set. Retrying...")
                # driver.save_screenshot(f"AMUL_debug_fail_attempt_{attempt+1}.png")  FOR DEBUGGING
            else:
                print(">> SUCCESS: Location verified!")
                # driver.save_screenshot("AMUL_debug_success_location.png") FOR DEBUGGING
                return True 
                
        except Exception as e:
            print(f">> Warning: Error during location set. ({e})")
            # --- SNAPSHOT ON ERROR ---
            # driver.save_screenshot(f"AMUL_debug_error_attempt_{attempt+1}.png")  FOR DEBUGGING
            # print(f">> Saved screenshot: AMUL_debug_error_attempt_{attempt+1}.png") FOR DEBUGGING
        
    print(">> CRITICAL: Could not set location after multiple attempts.")
    time.sleep(5)
    return False

def check_stock(driver):
    print(f">> Checking Stock: {ITEM_URL}")
    driver.get(ITEM_URL)
    time.sleep(5)
    
    try:
        xpath_in_stock = '//a[@title="Add to Cart"][@disabled="0"]'
        xpath_notify = '//a[@title="Add to Cart"][@disabled="true"]'

        # Check for In Stock
        if len(driver.find_elements(By.XPATH, xpath_in_stock)) > 0:
            print("   DEBUG: Add button is enabled (IN STOCK).")
            return True

        # Check for Out of Stock
        if len(driver.find_elements(By.XPATH, xpath_notify)) > 0:
            print("   DEBUG: Add button is disabled (Out of Stock).")
            return False

        print("   DEBUG: No buttons found (Layout Issue?).")
        return False

    except Exception as e:
        print(f"   Error: {e}")
        return False
    
def send_phone_notification():
    """Sends a push notification to your phone via ntfy.sh"""
    print(">> Sending Phone Notification...")
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data="🚨 AMUL ALERT: Item is IN STOCK! Go buy it now!",
            headers={
                "Title": "Amul Stock Alert",
                "Priority": "high",
                "Tags": "rotating_light,shopping_cart"
            }
        )
        print(">> Notification sent successfully!")
    except Exception as e:
        print(f"!! Failed to send notification: {e}")

        

def main():
    get_config()

    driver = init_browser()
    try:
        # 1. Setup Location first
        success = inject_and_validate_location(driver)
        
        if not success:
            print("Exiting because location could not be set manually.")
            return

        # 2. Start Monitoring Loop
        while True:
            if check_stock(driver):
                print("\n🚨🚨 IN STOCK 🚨🚨")
                
                send_phone_notification()
                break
            
            wait = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
            print(f"Waiting {wait}s...")
            time.sleep(wait)

    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()