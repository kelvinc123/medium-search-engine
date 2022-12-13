"""Scraper program to scrape medium article"""

import os
import sys
import time
import random
import multiprocessing
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Facebook Credentials
EMAIL = "..."
PASSWORD = "..."

DATA_PATH = os.path.join("dataset", "medium_data.csv")
HTML_PATH = os.path.join("dataset", "html")
CHROMEDRIVER_PATH = "chromedriver"
BASE_URL = "https://medium.com"
TIMEOUT_LIMIT = 60
PAGE_TIMEOUT = TIMEOUT_LIMIT // 10

def sleep_time(i):
    init_sleep = random.randint(5, 10) + random.randrange(0, 1)
    init_sleep += PAGE_TIMEOUT

    time.sleep(init_sleep)

def wait_by_xpath(driver, xpath, time_limit):
    try:
        WebDriverWait(driver, time_limit).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        sleep_time(1)
    except TimeoutException:
        print(f'Page timed out after {time_limit} secs')

def handle_login(driver, base_url, email, password, time_limit):
    driver.get(base_url)
    wait_by_xpath(driver, "//a[contains(text(), 'Sign In')]", time_limit)
    driver.find_element_by_xpath("//a[contains(text(), 'Sign In')]").click()
    wait_by_xpath(driver, "//div[contains(text(), 'Sign in with Facebook')]", time_limit)
    driver.find_element_by_xpath("//div[contains(text(), 'Sign in with Facebook')]").click()
    wait_by_xpath(driver, "//button[@id='loginbutton']", time_limit)
    driver.find_element_by_xpath("//input[@id='email']").send_keys(email)
    driver.find_element_by_xpath("//input[@id='pass']").send_keys(password)
    driver.find_element_by_xpath("//button[@id='loginbutton']").click()

def start():
    if not os.path.exists(DATA_PATH):
        print("Error!! data path doesn't exist")
        sys.exit(1)

    if not os.path.exists(HTML_PATH):
        os.mkdir(HTML_PATH)

    # Read dataset
    df = pd.read_csv(DATA_PATH)

    # Start driver
    driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    handle_login(driver, BASE_URL, EMAIL, PASSWORD, TIMEOUT_LIMIT)

    i = 0
    for row in df.iterrows():

        i += 1
        _id = row[1]["id"]
        filename = os.path.join(HTML_PATH, str(row[1]["id"]) + ".html")
        if os.path.exists(filename):
            # print(f"Path {filename} already exists!")
            continue
            
        
        print(f"Working on id:{_id}")
        # Get to the website
        url = row[1]["url"]
        driver.get(url)

        # Sleep for politeness
        sleep_time(i)

        # Parse and save html
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        with open(filename, "w") as f:
            f.write(soup.prettify())
        print(f"Successfully writes data to {filename}")

if __name__ == "__main__":

    timeout = False
    if timeout:
        p = multiprocessing.Process(target=start, name="Scraper")
        p.start()

        # Wait ___ seconds for start
        time.sleep(59 * 60)
        print("Time's up! Exitting!")

        # Terminate start
        p.terminate()

        # Cleanup
        p.join()

    else:
        start()