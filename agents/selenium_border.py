from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os 
class SeleniumBorder:

    connote=''


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
        self.quiet_batch_process_logger.info(f"Trying to login to Border...")
        print(f"Trying to login to Border...")

        try:
            username_textfield = self.driver.find_element(By.NAME,'Username')
            username_textfield.send_keys(os.environ['BEX_USERNAME'])

            password_textfield = self.driver.find_element(By.NAME,'Password')
            password_textfield.send_keys(os.environ['BEX_PASSWORD'])
            
            time.sleep(3)

            login_button = self.driver.find_element(By.ID,'button')
            login_button.click()
            
            
            # self.driver.get(redirect_url)
            # time.sleep(3)

            self.quiet_batch_process_logger.info(f"Login Successful...")
            print(f"Login Successful...")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")
    def fetch_connotes_from_history(self):
        time.sleep(3)
        self.quiet_batch_process_logger.info(f"Starting process")
        history_url = os.environ['BEX_HISTORY_URL']
        try:
            self.driver.get(history_url)
            time.sleep(3)
            self.quiet_batch_process_logger.info(f"On history page")
            print(f"On history page")
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")
        end_month = datetime.date.today()
        start_month = end_month - datetime.timedelta(days=60)
        current_date = start_month
        all_consignments = []

        while current_date <= end_month:
            # For 2-day intervals, adjust timedelta days accordingly for 3-day intervals
            end_date = current_date + datetime.timedelta(days=2)
            
            # If end_date goes beyond end_month, set it to end_month
            if end_date > end_month:
                end_date = end_month

            consignments = self.perform_search_history(current_date.strftime('%d/%m/%Y 12:00:00 AM'), end_date.strftime('%d/%m/%Y 12:00:00 AM'))
            self.driver.switch_to.default_content()
            all_consignments.extend(consignments)
            
            # Move to the next interval
            current_date = end_date + datetime.timedelta(days=1)
        return all_consignments

    def perform_search_history(self,start_date,end_date):
        time.sleep(5)
        try: 
            content_frame = self.driver.find_element(By.ID,'legacy-iframe')
            self.driver.switch_to.frame(content_frame)
            from_date_field = self.driver.find_element(By.ID,'From')
            from_date_field.clear()
            time.sleep(2)
            from_date_field.send_keys(start_date)
            time.sleep(2)

            to_date_field = self.driver.find_element(By.ID,'To')


            to_date_field.clear()

            time.sleep(2)
            to_date_field.send_keys(end_date)
            time.sleep(2)
            self.quiet_batch_process_logger.info(f"Dates and times entered")
            print(f"Dates and times entered")
            search_button = self.driver.find_element(By.ID,'btn-search')


            search_button.click()

            self.quiet_batch_process_logger.info(f"Search button clicked")
            print(f"Search button clicked")
            time.sleep(20)
            consignments = []
            while True:
                # Extract data from the current page (your extraction logic here)
                table_rows = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//table//tr"))
                )
                
                second_table = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "(//table)[2]"))  # XPath to select the second table
                )

                # Extracting rows from the second table
                table_rows = second_table.find_elements(By.TAG_NAME, "tr")
                
                # Extracting consignment numbers and dates using only Selenium
                
                for row in table_rows[1:]:  # [1:] is to skip the header row
                    columns = row.find_elements(By.TAG_NAME, "td")
                    if len(columns) > 2:
                        consignment_number = columns[1].text
                        consignment_date = columns[4].text
                        consignments.append((consignment_number, consignment_date))

                # Check for the "Next" button
                try:
                    next_button = self.driver.find_element(By.XPATH, '//a[@title="Go to the next page"]') 

                    # Check if the button is disabled by looking for the "k-state-disabled" class
                    if 'k-state-disabled' in next_button.get_attribute('class'):
                        break

                    # Click the button to go to the next page
                    next_button.click()
                    
                    # Wait for the next page to load (adjust the waiting logic as needed)
                    time.sleep(3)

                except Exception as err:
                    self.quiet_batch_process_logger.error(f"Error : {err}")
                    print(f"Error : {err}")
                    break

           
            # Log the extracted consignments
            self.quiet_batch_process_logger.info(f"Extracted Consignments: {consignments}")
            print(f"Extracted Consignments: {consignments}")
            return consignments

            
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")

    def perform_search(self,connote):
        time.sleep(3)

        self.quiet_batch_process_logger.info(f"Starting search for Connote : {connote}")
        print(f"Starting search for Connote : {connote}")

        search_url = os.environ['BEX_SEARCH_URL']

        try:
    
            # textbar = self.driver.find_element(By.ID,'qtSearchInput')
            # textbar.send_keys(connote)
            # textbar.click()

            # time.sleep(3)

            # search_button = self.driver.find_element(By.ID,'qtSearchButton')
            # search_button.click()
    
            print(search_url+connote)
            if(len(connote) != 0):
                self.driver.get(search_url+connote)
                time.sleep(3)
            else:
                return

            self.quiet_batch_process_logger.info(f"Search Complete...")
            print(f"Search Complete...")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")

        time.sleep(5)

        try:
            self.quiet_batch_process_logger.info(f"Opening the connote : {connote}")
            print(f"Opening the connote : {connote}")

           
            content_frame = self.driver.find_element(By.ID,'legacy-iframe')
            self.driver.switch_to.frame(content_frame)

            # Find the first row inside the table
            selection = self.driver.find_element(By.ID, "pnl-instruct")
            
            self.driver.execute_script("arguments[0].scrollIntoView();", selection)
            # Click on the first row
            selection.click()

            self.quiet_batch_process_logger.info(f"Timeslot Successfully opened : {connote}")
            print(f"Timeslot Successfully opened : {connote}")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")

    
    def extract_details(self,connote):
    
        self.quiet_batch_process_logger.info(f"Starting details Extraction for Connote : {connote}")
        print(f"Starting details Extraction for Connote : {connote}")

        try:
            # Locate the <td> element with the class "gw-label" and text "Date"
            date_td = self.driver.find_element(By.XPATH,"//td[@class='gw-label' and text()='Date']")
            date_value = date_td.find_element(By.XPATH,"following-sibling::td")
            date_text = date_value.text

            time_td = self.driver.find_element(By.XPATH,"//td[@class='gw-label' and text()='Time']")
            time_value = time_td.find_element(By.XPATH,"following-sibling::td")
            time_text = time_value.text

            self.quiet_batch_process_logger.info(f"Details Extracted for Connote : {connote} => {date_text} {time_text}")
            print(f"Details Extracted for Connote : {connote} => {date_text} {time_text}")

            return [date_text,time_text]
        
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")
            print(f"Error : {err}")

    
    def map_events(self,event):

        event_mapping = {
        "Delivered": "DEL",
        "Out for delivery": "OBFD",
        "Arrived Receiving Depot": "TRANSIT",
        "Estimated Arrival Receiving Depot":"TRANSIT",
        "Picked up from customer premises": "PICKUP",
        "Departed sending depot": "TRANSIT",
        }

        try:
            if(event in event_mapping):
                self.quiet_batch_process_logger.info(f"Mapping for event: {event} : {event_mapping[event]}")
                return event_mapping[event]
            else:
                self.quiet_batch_process_logger.info(f"Mapping for event: {event} : {event}")
                return ""

            

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

    def map_events_time(self,event):

        event_mapping_time = {
        "Delivered": "10:00 AM",
        "Out for delivery": "09:00 AM",
        "Arrived Receiving Depot": "10:00 AM",
        "Estimated Arrival Receiving Depot":"10:00 AM",
        "Picked up from customer premises": "12:00 PM",
        "Departed sending depot": "06:00 PM",
        }

        try:
            if(event in event_mapping_time):
                self.quiet_batch_process_logger.info(f"Mapping for event: {event} : {event_mapping_time[event]}")
                return event_mapping_time[event]
            else:
                self.quiet_batch_process_logger.info(f"Mapping for event: {event} : {event}")
                return ""

            

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

    def close_browser(self):
        self.driver.quit()
