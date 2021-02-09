from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from argparse import Namespace
from fake_useragent import UserAgent
import modules.config as g

def initialise_driver(args: Namespace) -> WebDriver:
    chrome_options = Options()
    ua = UserAgent()
    chrome_options.add_argument("user-agent=" + ua.random)
    chrome_options.add_argument('disable-infobars')
    if args.show == True:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("user-data-dir=" + g.DATA_DIR + "/selenium")
    chrome_options.add_experimental_option(
        'prefs',
        {
            "download.default_directory": g.DOWNLOAD_PATH,
            "download.prompt_for_download": False,
            # "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        },
    )
    try:
        browser = Chrome(
            executable_path=g.PATH_TO_CHROMEDRIVER, options=chrome_options,
        )
    except:
        # Assumes chromedriver is in path.
        browser = Chrome(
             options=chrome_options
        )
    return browser
