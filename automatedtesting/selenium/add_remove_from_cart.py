#!/usr/bin/env python3
"""
Selenium Functional UI Tests — Add/Remove All Items From Cart
Tests https://www.saucedemo.com

Rubric requirements:
  - Log in as a specific user
  - Add all 6 products to the cart (print each one)
  - Remove all 6 products from the cart (print each one)

Print output is captured by the CI/CD pipeline and written to selenium.log.
Log file must be UTF-8 so Azure Log Analytics can ingest it.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import datetime

# -------------------------------------------------------------------
# Logging — UTF-8 required for Azure Log Analytics ingestion
# -------------------------------------------------------------------
logging.basicConfig(
    filename='selenium.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver


def login(driver, username='standard_user', password='secret_sauce'):
    driver.get('https://www.saucedemo.com/')
    driver.find_element(By.ID, 'user-name').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'login-button').click()
    WebDriverWait(driver, 10).until(EC.url_contains('inventory'))
    msg = f'[CART TEST] User "{username}" logged in successfully.'
    print(msg)
    logger.info(msg)


def get_cart_count(driver):
    badges = driver.find_elements(By.CLASS_NAME, 'shopping_cart_badge')
    return int(badges[0].text) if badges else 0


def test_add_all_items(driver):
    """Add all 6 products to the cart, printing each one."""
    print('\n[CART TEST] --- Adding all items to cart ---')
    logger.info('[CART TEST] --- Adding all items to cart ---')

    driver.get('https://www.saucedemo.com/inventory.html')
    items = driver.find_elements(By.CLASS_NAME, 'inventory_item')

    added = []
    for item in items:
        name = item.find_element(By.CLASS_NAME, 'inventory_item_name').text
        btn  = item.find_element(By.CSS_SELECTOR, 'button[id^="add-to-cart"]')
        btn.click()
        added.append(name)
        msg = f'[CART TEST] Added to cart: "{name}"'
        print(msg)
        logger.info(msg)

    cart_count = get_cart_count(driver)
    assert cart_count == len(items), \
        f'Expected {len(items)} items in cart badge, got {cart_count}'

    summary = f'[CART TEST] PASS — {cart_count} items added to cart. Items: {added}'
    print(summary)
    logger.info(summary)
    return added


def test_remove_all_items(driver, added_items):
    """Remove all items from the cart page, printing each one."""
    print('\n[CART TEST] --- Removing all items from cart ---')
    logger.info('[CART TEST] --- Removing all items from cart ---')

    # Navigate to cart page
    driver.find_element(By.CLASS_NAME, 'shopping_cart_link').click()
    WebDriverWait(driver, 10).until(EC.url_contains('cart'))

    removed = []
    # Loop until no remove buttons remain
    while True:
        remove_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[id^="remove"]')
        if not remove_buttons:
            break
        # Get the item name before clicking remove
        cart_items = driver.find_elements(By.CLASS_NAME, 'cart_item')
        item_name = cart_items[0].find_element(By.CLASS_NAME, 'inventory_item_name').text
        remove_buttons[0].click()
        removed.append(item_name)
        msg = f'[CART TEST] Removed from cart: "{item_name}"'
        print(msg)
        logger.info(msg)

    cart_count = get_cart_count(driver)
    assert cart_count == 0, \
        f'Expected empty cart (0), got {cart_count}'
    assert len(removed) == len(added_items), \
        f'Expected to remove {len(added_items)} items, removed {len(removed)}'

    summary = f'[CART TEST] PASS — All {len(removed)} items removed. Items removed: {removed}'
    print(summary)
    logger.info(summary)


def main():
    header = '=' * 55
    print(header)
    print(f'  Selenium Cart Tests   |  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(header)
    logger.info(header)
    logger.info('Selenium Cart Tests started at %s', datetime.datetime.now().isoformat())
    logger.info(header)

    driver = get_driver()
    failed = 0
    try:
        login(driver)
        added = test_add_all_items(driver)
        test_remove_all_items(driver, added)
    except AssertionError as e:
        msg = f'[FAIL] {e}'
        print(msg)
        logger.error(msg)
        failed += 1
    except Exception as e:
        msg = f'[ERROR] Unexpected: {e}'
        print(msg)
        logger.error(msg)
        failed += 1
    finally:
        driver.quit()
        logger.info('[CART TEST] Browser closed.')

    summary = f'\nCart Tests Complete — Passed: {1 - failed} | Failed: {failed}'
    print(summary)
    logger.info(summary)
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
