from agents.selenium_tfm import SeleniumTfm
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import os
class Tfm:

    def __init__(self,cursor,conn):
        self.conn = conn
        self.cursor = cursor

    url = os.environ['TFM_LOGIN_URL']  

    def login(self):
         # Initialize your SeleniumBorder class with the connote value
        selenium_tfm = SeleniumTfm(self.url, quiet_batch_process_logger)
        selenium_tfm.open_website()
        selenium_tfm.login()
        return selenium_tfm
    
    def close_browser(self, selenium_tfm):
        
        selenium_tfm.close_browser()
    
    def process_timeslots(self, selenium_tfm,connote):
        timeslot = selenium_tfm.get_timeslot(connote)
        quiet_batch_process_logger.info(f"TFM: Timeslots Processed...")
        return timeslot
        
    def retrieve_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"TFM: Retrieving recordsfrom DB...")
        print('TFM: Retrieving recordsfrom DB...')

        try:
            query = f"SELECT [CarrierName],[ConnoteNumber],[DeliveryCompany],[TimeslotDate],[TimeslotTime],[IsHazardous],[Id],[PickupDate],[DataRunTime] FROM [dbo].[tmp_TFMTimeslots]"
            cursor.execute(query)
            records = [record[1] for record in cursor.fetchall()]

            quiet_batch_process_logger.info(f"TFM: Records Retrieved...")
            print(records)

            return records
        except Exception as e:
            print(e)
            quiet_batch_process_logger.error(f"TFM: Error : {e}")
    def delete_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"TFM: Deleting recordsfrom DB...")
        print('TFM: Deleting recordsfrom DB...')

        try:
            query = f"DELETE FROM [dbo].[tmp_TFMTimeslots]"
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(e)
            quiet_batch_process_logger.error(f"TFM: Error : {e}")
    def count_if_records_exists(self, cursor):
        # Count number of records that exist in database
        
        quiet_batch_process_logger.info(f"TFM: Checking if records exist for search purpose...")

        try:
            query = f"Select COUNT([ConnoteNumber]) FROM [dbo].[tmp_TFMTimeslots]"
            cursor.execute(query)
            records = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"TFM: Existing Records Counted...")
            return records

        except Exception as e:
            quiet_batch_process_logger.error(f"TFM: Error : {e}")
    def run_stored_procedure(self, cursor):
        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"TFM: Running Stored Procedure to find more records...")

        try:

            query = f"Execute TFMTimeslotConsignments"
            cursor.execute(query)
            self.conn.commit()
            print('TFM: Stored Procedure run finish...')
            quiet_batch_process_logger.info(f"TFM TimeSlot: Stored Procedure run finish...")
            
        except Exception as e:
            print("TFM: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"TFM: Error : {e}")