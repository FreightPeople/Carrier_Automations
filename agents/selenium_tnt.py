from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

class SeleniumTnt:
     
     
    def __init__(self, url,  logger):

        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
         
        self.url = url
        self.quiet_batch_process_logger = logger

    def open_website(self):
        try:    
            self.driver.get(self.url)
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
    
    def get_ETA(self,connote):
        close_cookie_bar = self.driver.find_element(By.CLASS_NAME, 'js-cookiebar-close')
        actions = ActionChains(self.driver)
        actions.move_to_element(close_cookie_bar).perform()
        close_cookie_bar.click()
        close_cookie_bar.click()
        connote_field = self.driver.find_element(By.ID, 'TextArea')
        connote_field.send_keys(connote)
        time.sleep(1)
        track_connote = self.driver.find_element(By.ID, 'bodycontent_btnSubmit')
        track_connote.click()
        time.sleep(3)
        try:
            ETA = self.driver.find_element(By.ID, 'bodycontent_explbl').text
            if(ETA == ''):
                ETA = None
            self.quiet_batch_process_logger.info(f"ETA for connote {connote} is {ETA}")
            print(f"ETA for connote {connote} is {ETA}")
            return ETA
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            return None


