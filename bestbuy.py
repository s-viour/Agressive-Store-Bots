import bs4
import sys
import time
import json
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service

# ---------------------------------------------Please Read--------------------------------------------------------------

# Updated: 6/15/2021

# Hello everyone! Welcome to my Best Buy script.
# Let's go over the checklist for the script to run properly.
#   1. Product URL
#   2. Firefox Profile
#   3. Credit Card CVV Number
#   4. Twilio Account (Optional)

# This Script only accepts Product URL's that look like this. I hope you see the difference between page examples.

# Example 1 - Nvidia RTX 3080:
# https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440
# Example 2 - PS5:
# https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149
# Example 3 - Ryzen 5600x:
# https://www.bestbuy.com/site/amd-ryzen-5-5600x-4th-gen-6-core-12-threads-unlocked-desktop-processor-with-wraith-stealth-cooler/6438943.p?skuId=6438943

# This Script does not accept Product URL's that look like this.
# https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys

# Highly Recommend To set up Twilio Account to receive text messages. So if bot doesn't work you'll at least get a phone
# text message with the url link. You can click the link and try manually purchasing on your phone.

# Twilio is free. Get it Here.
# www.twilio.com/referral/BgLBXx

# -----------------------------------------------Steps To Complete------------------------------------------------------

try:
    config_file = open('./config.json')
    config = json.loads(config_file.read())
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f'invalid or nonexistent config file: {e}')
    raise SystemExit

test_mode = config['testMode']
headless_mode = config['headlessMode']
webpage_refresh_timer = config['webpageRefreshTimer']
browser_type = config['browserType']
url = config['url']
cvv = config['cvv']
toNumber = config['twToNumber']
fromNumber = config['twFromNumber']
accountSid = config['twAccountSid']
authToken = config['twAuthToken']
chrome_executable_path = config['chromeExecutablePath']
chrome_data_path = config['chromeDataPath']
firefox_profile_path = config['firefoxProfilePath']


client = Client(accountSid, authToken)

def create_driver_firefox():
    """Creating firefox driver to control webpage. Please add your firefox profile down below."""
    options = FirefoxOptions()
    options.headless = headless_mode
    profile = webdriver.FirefoxProfile(firefox_profile_path)
    web_driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return web_driver

def create_driver_chrome():
    options = ChromeOptions()
    options.binary_location = chrome_executable_path
    print(f'chrome executable path is {chrome_executable_path}')
    print(f'chrome data path is {chrome_data_path}')
    options.headless = headless_mode
    options.add_argument(f'user-data-dir={chrome_data_path}')
    serv = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=serv, options=options)
    return driver

def create_driver():
    if browser_type == 'chrome':
        return create_driver_chrome()
    elif browser_type == 'firefox':
        return create_driver_firefox()
    print(f'invalid browser type supplied {browser_type}')
    raise SystemExit

# ----------------------------------------------------------------------------------------------------------------------


def time_sleep(x, driver):
    """Sleep timer for page refresh."""
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('Monitoring Page. Refreshing in{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.execute_script('window.localStorage.clear();')
    driver.refresh()


def extract_page():
    """bs4 page parser."""
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def driver_click(driver, find_type, selector):
    """Driver Wait and Click Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'xpath':
            try:
                driver.find_element_by_xpath(f"//*[@class='{selector}']").click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)


def searching_for_product(driver):
    """Scanning for product."""
    driver.get(url)

    print("\nWelcome To Bestbuy Bot! Join The Discord To find out What Week Bestbuy drops GPU's and Consoles!")
    print("Discord: https://discord.gg/qQDvwT6q3e")
    print("Donations keep the script updated!\n")
    print("Cashapp Donation: $TreborNamor")
    print("Bitcoin Donation: 16JRvDjqc1HrdCQu8NRVNoEjzvcgNtf6zW ")
    print("Dogecoin Donation: DSdN7qR1QR5VjvR1Ktwb7x4reg7ZeiSyhi \n")
    print("Bot deployed!\n")

    while True:
        soup = extract_page()
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 5)

        try:
            add_to_cart_button = soup.find('button', {
                'class': 'add-to-cart-button'
            })

            if add_to_cart_button:
                print(f'Add To Cart Button Found!')

                # Queue System Logic.
                try:
                    # Entering Queue: Clicking "add to cart" 2nd time to enter queue.
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                    driver_click(driver, 'css', '.add-to-cart-button')
                    print("Clicked Add to Cart Button. Now sending message to your phone.")
                    print("You are now added to Best Buy's Queue System. Page will be refreshing. Please be patient. It could take a few minutes.\n")

                    # Sleep timer is here to give Please Wait Button to appear. Please don't edit this.
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(5)
                except (NoSuchElementException, TimeoutException) as error:
                    print(f'Queue System Error: ${error}')

                # Sending Text Message To let you know you are in the queue system.
                try:
                    client.messages.create(to=toNumber, from_=fromNumber,
                                           body=f'Your In Queue System on Bestbuy! {url}')
                except (NameError, TwilioRestException):
                    pass

                # In queue, just waiting for "add to cart" button to turn clickable again.
                # page refresh every 15 seconds until Add to Cart button reappears.
                # Don't worry about people saying you'll losing your space in line if you refresh page.
                # I've tested this bot plenty times and it is not true. You can test the bot to find out.
                # When bot clicks "Add to Cart" button, a request is sent to server, and server is just waiting for a response.
                # No possible way to lose your spot once request is sent.
                while True:
                    try:
                        add_to_cart = driver.find_element_by_css_selector(".add-to-cart-button")
                        please_wait_enabled = add_to_cart.get_attribute('aria-describedby')

                        if please_wait_enabled:
                            driver.refresh()
                            time.sleep(15)
                        else:  # When Add to Cart appears. This will click button.
                            print("Add To Cart Button Clicked A Second Time.\n")
                            wait2.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button")))
                            time.sleep(2)
                            driver_click(driver, 'css', '.add-to-cart-button')
                            time.sleep(2)
                            break
                    except(NoSuchElementException, TimeoutException) as error:
                        print(f'Queue System Refresh Error: ${error}')

                # Going To Cart Process.
                driver.get('https://www.bestbuy.com/cart')

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    time.sleep(1)
                    driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary')
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    time_sleep(3, driver)
                    searching_for_product(driver)

                # Logging Into Account.
                print("\nAttempting to Login. Firefox should remember your login info to auto login.")
                print("If you're having trouble with auto login. Close all firefox windows.")
                print("Open firefox manually, and go to bestbuy's website. While Sign in, make sure to click 'Keep Me Logged In' button.")
                print("Then run bot again.\n")

                # Click Shipping Option. (if available)
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    time.sleep(2)
                    shipping_class = driver.find_element_by_xpath("//*[@class='ispu-card__switch']")
                    shipping_class.click()
                    print("Clicking Shipping Option.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as error:
                    print(f'shipping error: {error}')

                # Trying CVV
                try:
                    print("\nTrying CVV Number.\n")
                    wait2.until(EC.presence_of_element_located((By.ID, "cvv")))
                    time.sleep(1)
                    security_code = driver.find_element_by_id("cvv")
                    time.sleep(1)
                    security_code.send_keys(cvv)
                except (NoSuchElementException, TimeoutException):
                    pass

                # Final Checkout.
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    # comment the one down below. vv
                    if not test_mode:
                        print("Product Checkout Completed.")
                        time.sleep(1)
                        driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary button__fast-track')
                    if test_mode:
                        print("Test Mode - Product Checkout Completed.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Complete Checkout.")

                # Completed Checkout.
                print('Order Placed!')
                time.sleep(1800)
                driver.quit()

        except (NoSuchElementException, TimeoutException) as error:
            print(f'error is: {error}')

        time_sleep(webpage_refresh_timer, driver)


if __name__ == '__main__':
    driver = create_driver()
    searching_for_product(driver)
