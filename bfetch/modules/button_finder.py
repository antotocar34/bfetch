from selenium.webdriver.remote.webelement import WebElement

from typing import List, Callable
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from .utils import get_request


def check_if_button_was_found(button: WebElement) -> bool:
    """
    Prints a confirmation if the button element
    was found.
    """
    if bool(button) is False:
        print("Button was not found")
        return False
    else:
        print(f"Button {button.text} was found")
        return True


def wait_condition(
        browser: WebDriver, args: List[str], associated_methods: List[Callable]
):
    """
    Returns a condition for the first argument specified.
    """
    for i, arg in enumerate(args):
        if arg != "":
            condition = associated_methods[i]
            return condition


def smart_wait(
    browser: WebDriver, args: List[str], associated_methods: List[Callable]
):
    """Waits until an element is found,
    TODO find out exactly what to do here.
    """
    cond = wait_condition(browser, args, associated_methods)
    try:
        WebDriverWait(browser, 3).until(cond)
    except TimeoutException:
        pass


def find_child_hrefs(button: WebElement) -> List[str]:
    children = button.find_elements_by_xpath(".//*")
    hrefs = []
    for child in children:
        try:
            href = child.get_attribute("href")
            hrefs.append(href)
        except:
            continue
    hrefs = [href for href in hrefs if href is not None]
    return hrefs


def find_button(browser: WebDriver, id_string: str ="", partial_link: str ="", name: str="", xpath: str =""):
    """browser -> [str] -> button

    Finds button by specifying one of the following:
    id, subset of text, or the name.
    """
    args = [id_string, partial_link, name, xpath]

    # functions should come in the same order as the args list.
    associated_methods = [
        lambda browser: browser.find_element_by_id(id_string),
        lambda browser: browser.find_element_by_partial_link_text(partial_link),
        lambda browser: browser.find_element_by_name(name),
        lambda browser: browser.find_element_by_xpath(xpath),
    ]

    print("waiting for button")
    smart_wait(browser, args, associated_methods)
    print("found it!")

    found_buttons = []
    for i, arg in enumerate(args):
        if arg != "":
            find_function = associated_methods[i]
            button = find_function(browser)
            foundBool = check_if_button_was_found(button)
            if foundBool == True:
                found_buttons.append(button)

    return found_buttons


def find_and_click_button(
        browser: WebDriver, id_string: str ="", partial_link: str ="", name: str ="", xpath: str = ""
) -> None:
    """
    Finds a button element and clicks it.

    At least one argument must be specified.
    Optional arguments are
    -> id class
    -> string that partially matches link
    -> name of the element
    -> xpath of the element
    """
    # Test that at least one optional argument was given.
    optional_args = [arg for arg in locals().values() if type(arg) == str]
    test = [bool(x) for x in optional_args]

    if any(test) == False:
        print("No optional arguments given for button!")
        raise Exception

    found_buttons = find_button(browser, id_string, partial_link, name, xpath)
    # wait for clickable wait function here?
    for button in found_buttons:
        try:
            button.click()
            break
        except:
            pass

        # If clicking the above fails, try to
        # Click any link in the child instances.
        # This may not be a great idea...
        hrefs = find_child_hrefs(button)
        for href in hrefs:
            try:
                get_request(browser, href)
                return
            except:
                pass
    else:
        print("No clickable button elements found! Stopping the program...")
        raise Exception

    return
