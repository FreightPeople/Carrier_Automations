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
            close_cookie_bar = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'js-cookiebar-close'))
            )
            self.driver.execute_script("arguments[0].click();", close_cookie_bar)
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
    
    def get_ETA(self,connote,id):
        #content_frame = self.driver.find_element(By.CLASS_NAME, 'cookieMessageIParsys iparsys parsys')
        #self.driver.switch_to.frame(content_frame)
        self.driver.get(self.url)


        try:
            # Locate the TextArea element
            connote_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'TextArea'))
            )
            # Enter text into the TextArea element


            connote_field.send_keys(connote)
            print("Entered text in the TextArea")
        except Exception as e:
            print(f"Error while interacting with the TextArea: {e}")
        try:
            # Wait for the button to be clickable
            track_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'bodycontent_btnSubmit'))
            )
            # Click the 'Track' button
            track_button.click()
            print("Clicked the 'Track' button")
        except Exception as e:
            print(f"Error while clicking the 'Track' button: {e}")
        try:
            # Wait for the element with the specified ID to be present in the DOM
            ETA_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'bodycontent_explbl'))
            )
            
            # Once the element is present, retrieve its text
            ETA = ETA_element.text.strip()  # Strip any leading/trailing whitespace
            
            if not ETA:  # Check if ETA is empty
                ETA = None
            print(f"ETA for connote {connote} is {ETA}")
            record = (connote, ETA,id)
            return record
        except Exception as err:
            print(f"Error at ETA getting: {err}")
            record = (connote, None , id)
            return record


