from agents.selenium_tnt import SeleniumTnt
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import pymssql
import os

class Tnt:

    def __init__(self,cursor,conn):
        self.conn = conn
        self.cursor = cursor

    url = 'https://www.tntexpress.com.au/interaction/trackntrace.aspx'


    def login(self):
         # Initialize your SeleniumBorder class with the connote value
        selenium_tnt = SeleniumTnt(self.url, quiet_batch_process_logger)
        selenium_tnt.open_website()
        return selenium_tnt
    
    def retreive_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"TNT: Retrieving recordsfrom DB...")
        print('TNT: Retrieving recordsfrom DB...')

        try:
            query = f"EXEC TNTActiveConsignments"
            cursor.execute(query)
            records = [record[1] for record in cursor.fetchall()]

            quiet_batch_process_logger.info(f"TNT: Records Retrieved...")
            print(records)

            return records
        except Exception as e:
            print(e)
            quiet_batch_process_logger.error(f"TNT: Error : {e}")

    def close_browser(self, selenium_tnt):
        selenium_tnt.close_browser()

    def get_web_ETA(self, selenium_tnt, connote):
        eta = selenium_tnt.get_ETA(connote)
        quiet_batch_process_logger.info(f"TNT: ETA Processed...")
        return eta
    
