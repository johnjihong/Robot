from __future__ import absolute_import
from Robot.log import logger
from typing import Callable
from seleniumrequests import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class is_page_read:
    def __call__(self, driver):
        is_dom_ready = driver.execute_script("return document.readyState === 'complete';")

        try:
            has_ajax_completed = driver.execute_script('return jQuery.active === 0;')
        except WebDriverException:
            logger.exception(exc_info=True)
            return is_dom_ready
        else:
            return is_dom_ready and has_ajax_completed


class Factory:
    def __init__(self, username: str, password: str, timeout: int=30, executable_path: str=None):
        self.username = username
        self.password = password
        self.timeout = timeout
        self.executable_path = executable_path if executable_path else 'phantomjs'

    def login(self, url):
        self.driver = PhantomJS(executable_path=self.executable_path)
        self.driver.get(url)
        self.driver.find_element_by_id('userID').send_keys(self.username)
        self.driver.find_element_by_id('password').send_keys(self.password)
        self.driver.find_element_by_xpath("//input[@value='Log in']").click()

        WebDriverWait(self.driver, self.timeout).until(
            EC.text_to_be_present_in_element((By.XPATH, "//a[@alt='logout']"), 'Log Out'),
            '%s failed to login within %d seconds timeout' % (self.username, self.timeout)
        )

    def start(self, method: Callable):
        method()

        WebDriverWait(self.driver, self.timeout).until(
            is_page_read(),
            'Opertation failed to be completed before the %d seconds timeout' % self.timeout
        )