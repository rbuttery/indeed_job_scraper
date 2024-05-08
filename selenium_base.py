from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time

# Database tools
from database_tools import DatabaseTools


class Browsers:
    CHROME = 'chrome'
    EDGE = 'edge'
    FIREFOX = 'firefox'


class SeleniumScraper:
    
    def __init__(self, browser:str=Browsers.CHROME, use_database:bool = False):
        self.database = DatabaseTools().setup() if use_database else None
        self.browser = browser
        self.options = None
        self.service = None
        self.current_url = None
        self.previous_url = None 
    
    """BROWSER SETUP"""
    def __setup_chrome(self):
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.options = ChromeOptions()

    def __setup_edge(self):
        self.service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
        self.options = EdgeOptions()

    def __setup_firefox(self):
        self.service = FirefoxService(executable_path=GeckoDriverManager().install())
        self.options = FirefoxOptions()

    def _setup_browser(self):
        print(f'Setting up {self.browser} browser...')
        browser_methods = {
            'chrome': self.__setup_chrome,
            'edge': self.__setup_edge,
            'firefox': self.__setup_firefox
        }
        setup_method = browser_methods.get(self.browser)
        if setup_method:
            setup_method()
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
       
        try:
            # Firefox doesnt have this option, helps reduce the amount of logs
            self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        except:
            pass
    
    def __open_chrome(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def __open_edge(self):
        self.driver = webdriver.Edge(service=self.service, options=self.options)

    def __open_firefox(self):
        self.driver = webdriver.Firefox(service=self.service, options=self.options)
    
    """BROWSER ACTIONS"""
    def open_browser(self, wait_seconds=0):
        self._setup_browser()
        print(f'Opening {self.browser} browser...')
        browser_methods = {
            'chrome': self.__open_chrome,
            'edge': self.__open_edge,
            'firefox': self.__open_firefox
        }
        open_method = browser_methods.get(self.browser)
        if open_method:
            open_method()
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
        if wait_seconds > 0:
            time.sleep(wait_seconds)
    
    def go_to_url(self, url):
        self.previous_url = self.current_url
        self.driver.get(url)
        self.current_url = url
    
    def close_browser(self):
        self.driver.close()
    
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0,1000000)")
