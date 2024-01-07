# Author: Gavin Kondrath | gav.ink
# Created on: Dec 27th, 2023

import datetime
import pytz
import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from urllib.parse import urlsplit
from dotenv import load_dotenv

from config import launcher_path

load_dotenv()
proton_user = os.environ['PROTON_USER']
proton_pass = os.environ['PROTON_PASS']

search_query = "Hidden_reddit"

timezone = pytz.timezone('US/Central')
current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

user_agents = [
        # macos firefox
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0",
        # macos safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        # macos chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # macos edge
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

        # windows chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        # windows edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

        # windows firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]

strategies = [
        "channel",
        "shorts"
        ]


def watch_youtube_videos(strategy):
    user_agent = random.choice(user_agents)
    driver_path = f'{launcher_path}/drivers/firefox/geckodriver'
    driver_service = Service(driver_path, log_output=f'{launcher_path}/temp/log.log')
    driver_option = Options()
    # driver_option.add_argument("-headless")
    driver_option.set_preference('general.useragent.override', user_agent)
    driver_option.set_preference("permissions.default.desktop-notification", 2)
    driver = webdriver.Firefox(options=driver_option, service=driver_service)
    driver.install_addon(f'{launcher_path}/drivers/firefox/protonvpn.xpi')

    driver.implicitly_wait(9)
    window_handles = driver.window_handles
    parent_tab = driver.window_handles[0]
    child_tab = driver.window_handles[1]
    wait = WebDriverWait(driver, 60)

    page_load_timeout = 60
    url = 'https://www.youtube.com/'
    browser_settings = 'about:addons'
    vpn_location = "United States"

    print("Setting up VPN")
    driver.set_window_size(1400, 1200)
    driver.get(browser_settings)
    time.sleep(.5)
    driver.switch_to.window(child_tab)
    extension_id = driver.current_url
    parsed_url = urlsplit(extension_id)
    extension_id = parsed_url.netloc
    print(extension_id)
    driver.switch_to.window(parent_tab)
    time.sleep(.5)
    extensions = driver.find_element(By.XPATH, '/html/body/div/div[1]/categories-box/button[2]')
    extensions.click()
    proton_options = driver.find_element(By.XPATH, "//*[contains(text(), 'Proton VPN:')]")
    proton_options.click()
    proton_perms = driver.find_element(By.XPATH, '//*[@id="details-deck-button-permissions"]')
    proton_perms.click()
    proton_control = driver.find_element(By.ID, "permission-0")
    driver.execute_script("arguments[0].click();", proton_control)
    proton_access_all = driver.find_element(By.ID, "permission-1")
    driver.execute_script("arguments[0].click();", proton_access_all)
    proton_access_com = driver.find_element(By.XPATH, '//*[@id="permission-2"]')
    proton_access_com.click()
    proton_access_me = driver.find_element(By.XPATH, '//*[@id="permission-3"]')
    proton_access_me.click()
    driver.switch_to.window(child_tab)
    proton_sign_in = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/button')
    proton_sign_in.click()
    time.sleep(2)  # increase if fails
    proton_login_tab = driver.window_handles[2]
    driver.switch_to.window(proton_login_tab)
    proton_email = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
    proton_email.click()
    proton_email.clear()
    for char in proton_user:
        proton_email.send_keys(char)
        delay = random.uniform(0.1, 0.2)
        time.sleep(delay)
    proton_password = driver.find_element(By.XPATH, '//*[@id="password"]')
    proton_password.click()
    proton_password.clear()
    for char in proton_pass:
        proton_password.send_keys(char)
        delay = random.uniform(0.1, 0.2)
        time.sleep(delay)
    proton_password.send_keys(Keys.ENTER)
    extension_url = f'moz-extension://{extension_id}/popup.html'
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Open the Proton VPN')]")))
    try:
        driver.set_page_load_timeout(page_load_timeout)
        driver.get(extension_url)
    except TimeoutException as e:
        driver.close()
        raise TimeoutError(f"Selenium timed out waiting for the page to load: {e}")

    proton_search = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-input"]')))
    time.sleep(1)
    proton_search.send_keys(vpn_location)
    proton_search.send_keys(Keys.ENTER)
    time.sleep(1)

    print("Connected to VPN")

    try:
        driver.set_page_load_timeout(page_load_timeout)
        driver.get(url)
    except TimeoutException as e:
        driver.close()
        raise TimeoutError(f"Selenium timed out waiting for the page to load: {e}")

    youtube_search_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-input"]')))
    youtube_search_input.click()
    youtube_search = driver.find_element(By.XPATH, '//input[@placeholder="Search"]')
    for char in search_query:
        youtube_search.send_keys(char)
        delay = random.uniform(0.1, 0.2)
        time.sleep(delay)
    time.sleep(0.5)
    youtube_search.send_keys(Keys.ENTER)

    click_delay = random.uniform(1, 3)
    watch_video = random.uniform(20, 40)

    # if search instead appears
    search_instead_xpath = "//*[starts-with(@href, '/results?search_query=Hidden_reddit')]"
    time.sleep(click_delay)

    try:
        search_instead = driver.find_element(By.XPATH, search_instead_xpath)
        if search_instead.is_displayed():
            search_instead.click()

        else:
            try:
                youtube_channel = driver.find_element(By.XPATH, '//a[@href="/@hidden_reddit"]')
                if youtube_channel.is_displayed():
                    strategy = "channel"
                    youtube_channel.click()

            except NoSuchElementException as e:
                print("Element not found:", e)

    except NoSuchElementException as e:
        print("Element not found:", e)

    if strategy == "channel":
        youtube_channel = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/@hidden_reddit"]')))
        time.sleep(click_delay)
        youtube_channel.click()

        # fix this not being interactable
        first_short_xpath = '(//ytd-reel-item-renderer)[1]'
        first_short = wait.until(EC.element_to_be_clickable((By.XPATH, first_short_xpath)))
        time.sleep(click_delay)
        first_short.click()
        time.sleep(watch_video)

        watch_counter = 1
        watch_max = random.randint(2, videos)
        print(watch_max)

        while True:
            down_button = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-shorts/div[5]/div[2]/ytd-button-renderer/yt-button-shape/button/yt-touch-feedback-shape/div')
            down_button.click()
            time.sleep(watch_video)
            watch_counter += 1

            if watch_counter == watch_max:
                break

    elif strategy == "shorts":
        first_short_xpath = '(//ytd-reel-item-renderer)[1]'

        try:
            first_short = wait.until(EC.element_to_be_clickable((By.XPATH, first_short_xpath)))
            if first_short.is_displayed():
                time.sleep(click_delay)
                first_short.click()

            else:
                try:
                    first_video_xpath = '(//ytd-video-renderer)[1]'
                    first_video = wait.until(EC.element_to_be_clickable((By.XPATH, first_video_xpath)))
                    if first_video.is_displayed():
                        time.sleep(click_delay)
                        first_video.click()

                except NoSuchElementException as e:
                    print("Element not found:", e)

        except NoSuchElementException as e:
            print("Element not found:", e)

        time.sleep(watch_video)

        watch_counter = 1
        watch_max = random.randint(2, videos)
        print(watch_max)

        while True:
            down_button = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-shorts/div[5]/div[2]/ytd-button-renderer/yt-button-shape/button/yt-touch-feedback-shape/div')
            down_button.click()
            time.sleep(watch_video)
            watch_counter += 1

            if watch_counter == watch_max:
                break

    if driver:
        for handle in window_handles:
            driver.switch_to.window(handle)
            driver.close()
        driver.quit()


watch_count = 1
videos = 30
strategy = "shorts"
# strategy = random.choice(strategies)
while True:
    watch_youtube_videos(strategy)
    watch_count += 1

    if watch_count == 500:
        break
