from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
class SeleniumTfm:
     
     
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

    def login(self):
        self.quiet_batch_process_logger.info(f"Trying to login to TFM...")
        print(f"Trying to login to TFM...")

        try:
            username_textfield = self.driver.find_element(By.NAME,'Username')
            username_textfield.send_keys(os.environ['TFM_USERNAME'])
            time.sleep(1)
            password_textfield = self.driver.find_element(By.NAME,'Password')
            password_textfield.send_keys(os.environ['TFM_PASSWORD'])

            time.sleep(1)

            login_button = self.driver.find_element(By.NAME,'button')
            login_button.click()
            
            time.sleep(3)

            # self.driver.get(redirect_url)
            # time.sleep(3)

            self.quiet_batch_process_logger.info(f"Login Successful...")
            print(f"Login Successful...")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")

    def get_timeslot(self, connote):
        
        content_frame = self.driver.find_element(By.ID, 'mainFrame')
        self.driver.switch_to.frame(content_frame)
        connote_field = self.driver.find_element(By.ID, 'Consignment')
        connote_field.clear()
        time.sleep(1)
        connote_field.send_keys(connote)
        time.sleep(2)
        view_connotefield = self.driver.find_element(By.ID, 'btnView')
        view_connotefield.click()
        time.sleep(3)
        
        # Check if there is a booking
        timeslot_field = self.driver.find_element(By.ID, 'aBooking')
        if 'Delivery Window (1)' in timeslot_field.text:
            print("Found a booking!")
            # Perform the actions to view the booking details
            # You might need to adjust the code here based on how your application shows the booking details
            timeslot_field.click()
            time.sleep(3)

            # Extract the required data
            # Replace 'your_table_selector' with the actual selector for your table
            table = self.driver.find_element(By.ID, 'tblGrid')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            booking_details = []
            # Skip the first row as it's the header
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 5:
                    # Extract text from  ('Delivery Date') and  ('To') 'td' elements
                    delivery_date_text = cells[1].text
                    # Remove any leading text, assuming it always starts with "On "
                    if delivery_date_text.startswith("On "):
                        delivery_date = delivery_date_text.split(" ")[1]
                    else:
                        delivery_date = delivery_date_text  # Fallback in case the format is not as expected
                    from_time = cells[2].text
                    booking_details.append((delivery_date, from_time))

                    print(f"{connote} booking details: {delivery_date}, {from_time}")
            self.driver.switch_to.default_content()
            
            return booking_details
        else:
            self.driver.switch_to.default_content()

            print("No bookings found.")
            return None
        

    def close_browser(self):
        self.driver.quit()
