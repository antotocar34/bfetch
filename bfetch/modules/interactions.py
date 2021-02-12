import getpass
from time import sleep
import sys
from typing import Tuple

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from bs4.element import Tag

from bfetch.modules.button_finder import find_and_click_button
from bfetch.modules.utils import make_soup, get_request


def init_login_info(
    browser: WebDriver, uname_form_id: str, pword_form_id: str
) -> Tuple[WebElement, WebElement]:
    """Finds login form."""
    username_form = browser.find_elements_by_id(uname_form_id)[0]
    password_form = browser.find_elements_by_id(pword_form_id)[0]
    return username_form, password_form


def type_login_info(browser: WebDriver,
                    uname_form: WebElement,
                    pword_form: WebElement) -> None:
    """Sends username and password to login form."""
    try:
        from bfetch.modules.secretss import username, password
    except:
        message_u = "Please enter your blackboard username."
        message_p = "Please enter you blackboard password."
        prompt = "> "
        username = input(message_u + "\n" + prompt)
        password = getpass.getpass(prompt=f"{message_p}\n{prompt}", stream=None) 

    uname_form.send_keys(username)
    pword_form.send_keys(password)


def log_in(browser: WebDriver):
    print("Get request for blackboard")
    get_request(browser, "https://tcd.blackboard.com/")
    print("Get request accepted")

    # Todo add redundancies.
    login_xpath = '//*[@id="learn-oe-body"]/div/header/a/button'

    print("Finding login button.")
    find_and_click_button(browser, xpath=login_xpath)

    print("Inputing username and password.")
    username_form, password_form = init_login_info(
        browser, "username", "password"
    )
    type_login_info(browser, username_form, password_form)

    try:
        find_and_click_button(browser, name="_eventId_proceed")
    except Exception as e:
        print(f"Could not find Login Button: {e}\n Exiting the Program...")
        sleep(2)
        sys.exit()
    print("Succesfully Logged In!")

    agree_button_id = "agree_button"
    try:
        # Lookout for agree to conditions button.
        # Press the agree to conditions button.
        find_and_click_button(browser, id_string=agree_button_id)
    except Exception as e:
        pass
    return

def click_module_list(browser: WebDriver):
    # Click the Module List
    find_and_click_button(
        browser, xpath="""//*[@id="Module List"]/a""", id_string="Module List"
    )
    # DO NOT REMOVE
    sleep(1)
