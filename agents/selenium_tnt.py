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
        #content_frame = self.driver.find_element(By.CLASS_NAME, 'cookieMessageIParsys iparsys parsys')
        #self.driver.switch_to.frame(content_frame)
        close_cookie_bar = self.driver.find_element(By.CLASS_NAME, 'js-cookiebar-close')
        self.driver.execute_script("arguments[0].click();", close_cookie_bar)
        self.quiet_batch_process_logger.info("Closed the cookie bar")
        time.sleep(1)
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


