from typing import Tuple
import requests

from selenium.webdriver.chrome.webdriver import WebDriver



def head_request(browser: WebDriver, url: str) -> Tuple[str,str]:
    cookies = browser.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    response = s.head(url, stream=True)
    # print(response.status_code)
    location = response.headers.get("Location")
    file_name = location.split("/")[-1].replace("%20", " ")
    filetype = location.split(".")[-1]
    print(file_name, filetype)
    return file_name, filetype

