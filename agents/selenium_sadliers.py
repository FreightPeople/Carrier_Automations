from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.firefox.options import Options

class SeleniumSadliers:

    connote=''


    def __init__(self, url, connote, logger):

        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(options=options)
        self.url = url
        self.connote = connote
        self.quiet_batch_process_logger = logger


    def open_website(self):

        try:    
            self.driver.get(self.url)
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

    def login(self):
        self.quiet_batch_process_logger.info(f"Trying to login to Sadliers...")

        try:
            username_textfield = self.driver.find_element(By.NAME,'Username')
            username_textfield.send_keys('302011')

            password_textfield = self.driver.find_element(By.NAME,'Password')
            password_textfield.send_keys('kerry3175')
            
            time.sleep(3)

            login_button = self.driver.find_element(By.CLASS_NAME,'app-LoginFormButton')
            login_button.click()
            
            self.quiet_batch_process_logger.info(f"Login Successful...")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")


    def perform_search(self):
        time.sleep(3)

        self.quiet_batch_process_logger.info(f"Starting search for Connote : {self.connote}")


        try:
    
            searchbar = self.driver.find_element(By.ID,'menu-advancedsearch')
            searchbar.click()

            connote_textfield = self.driver.find_element(By.ID,'ConsignmentNumber')
            connote_textfield.send_keys(self.connote)
            
            time.sleep(3)

            search_button = self.driver.find_element(By.ID,'btnSearch')
            search_button.click()
    
            self.quiet_batch_process_logger.info(f"Search Complete...")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

        time.sleep(5)

        try:
            self.quiet_batch_process_logger.info(f"Opening the connote : {self.connote}")

            # Find the first row inside the table
            selection = self.driver.find_element(By.LINK_TEXT, str(self.connote))
            
            self.driver.execute_script("arguments[0].scrollIntoView();", selection)

            # Click on the first row
            selection.click()

            self.quiet_batch_process_logger.info(f"Connote Successfully opened : {self.connote}")

        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

    
    def extract_details(self):
    
        self.quiet_batch_process_logger.info(f"Starting details Extraction for Connote : {self.connote}")

        try:
            # Find the element with the text "History" within an h3 tag
            history_title_element = self.driver.find_element(By.XPATH, '//h3[text()="History"]')
            self.driver.execute_script("arguments[0].scrollIntoView();", history_title_element)
            
            time.sleep(3)

            # Navigate to the parent div containing the table
            title_container = history_title_element.find_element(By.XPATH, './parent::div')

            table_container = title_container.find_element(By.XPATH, './parent::div')

            # Find the table within the container
            table_element = table_container.find_element(By.CLASS_NAME, 'jsgrid-table')

            # Find all rows within the table body
            rows = table_element.find_elements(By.XPATH, './/tbody/tr')

            # Initialize empty lists to store the extracted data
            statuses = []
            dates = []
            locations = []

            # Loop through each row and extract data
            statusEvents=[]
            for row in rows:
                cells = row.find_elements(By.XPATH, './/td')
                status = cells[0].text
                date = cells[1].text
                location = cells[2].text
                
                statuses.append(status)
                dates.append(date)
                locations.append(location)

            # Print the extracted data
            for i in range(len(statuses)):
                statusEvents.append({"connote":self.connote, "eventtype":self.map_events(statuses[i]), "date":dates[i], "time":self.map_events_time(statuses[i]),"location":locations[i],"extrainfo":statuses[i]})
                print(f"{statusEvents}")

            self.quiet_batch_process_logger.info(f"Detail Extraction Finished...")

            return statusEvents
            
        
        except Exception as err:
            self.quiet_batch_process_logger.error(f"Error : {err}")

    
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
