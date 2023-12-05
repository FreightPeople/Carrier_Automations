from agents.selenium_sadliers import SeleniumSadliers  # Import your SeleniumTGE class
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import os
class Sadleirs:

    def __init__(self, cursor, conn):
        
        self.conn = conn
        self.cursor = cursor
       

    url = os.environ['SADLEIRS_LOGIN_URL'] 

    def retrieve_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"Sadleirs: Retrieving recordsfrom DB...")

        try:
            query = f"Select [CarrierName], [ConnoteNumber] ,[DeliveryCompany] ,[IsHazardous] FROM [dbo].[tmp_SadleirsConsignments]"
            cursor.execute(query)
            records = [record[1] for record in cursor.fetchall()]

            quiet_batch_process_logger.info(f"Sadleirs: Records Retrieved...")
            print(records)

            return records
        
        except Exception as e:
            print(e)

            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")


        

    def count_if_records_exists(self, cursor):
        # Count number of records that exist in database
        
        quiet_batch_process_logger.info(f"Sadleirs: Checking if records exist for search purpose...")

        try:
            query = f"Select COUNT([ConnoteNumber]) FROM [dbo].[tmp_SadleirsConsignments]"
            cursor.execute(query)
            records = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"Sadleirs: Existing Records Counted...")
            return records

        except Exception as e:
            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")


        
    def run_stored_procedure(self, cursor):
        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"Sadleirs: Running Stored Procedure to find more records...")

        try:

            query = f"Execute SadleirsConsignments_Kerry"
            cursor.execute(query)
            self.conn.commit()

            quiet_batch_process_logger.info(f"Sadleirs: Stored Procedure run finish...")
            
        except Exception as e:
            print("Sadleirs: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")




    def process_record(self, connote):
        # Initialize your SeleniumSadliers class with the connote value
        selenium_sadliers = SeleniumSadliers(self.url, connote, quiet_batch_process_logger)
        selenium_sadliers.open_website()
        selenium_sadliers.login()
        selenium_sadliers.perform_search()
        statusEvents = selenium_sadliers.extract_details()
        
        selenium_sadliers.close_browser()

        quiet_batch_process_logger.info(f"Sadleirs: Record Processed for Connote : {connote}")


        return statusEvents

    def save_record(self, cursor, connote, statusEvents):
        try:

            for status in statusEvents:
                
                count_query = f"SELECT COUNT([ConnoteNumber]) from [dbo].[SadleirsEvents] WHERE [ConnoteNumber] = '{status['connote']}' and [EventType] = '{status['eventtype']}' and [EventDate]='{status['date']}' and [Location] = '{status['location']}'"
                print("Sadleirs: Update Query:", count_query)

                cursor.execute(count_query)
                count = cursor.fetchone()[0]

                quiet_batch_process_logger.info(f"Sadleirs: Count of available connote (check flag if connote already exisits): {count}")


                if(count==0):

                    insert_query = f"INSERT INTO [dbo].[SadleirsEvents] ([ConnoteNumber], [EventType], [EventDate], [EventTime], [Location], [ExtraInfo]) VALUES ('{status['connote']}', '{status['eventtype']}' , '{status['date']}' , {status['time']}, '{status['location']}','{status['extrainfo']}');"
                    print("Sadleirs: Update Query:", insert_query)

                    cursor.execute(insert_query)
                    self.conn.commit()  # Commit the transaction to save the changes

                    print("Sadleirs: Update successful.")
                    quiet_batch_process_logger.info(f"Sadleirs: Events table has been updated...")


            
        except Exception as e:
            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")

            print("Sadleirs: Error:", e)
            self.conn.rollback()

    def delete_record(self, cursor, connote):

        try:
            delete_query = f"DELETE FROM [dbo].[tmp_SadleirsConsignments] WHERE [ConnoteNumber]='{connote}'"
            print("Sadleirs: Delete Query:", delete_query)

            cursor.execute(delete_query)
            self.conn.commit()  # Commit the transaction to save the changes
            quiet_batch_process_logger.info(f"Sadleirs: Record for {connote} deleted from temp table...")

            print("Sadleirs: Delete successful.")

            
        except Exception as e:
            print("Sadleirs: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")


    def RunStoredProcedureToCreatePublishFile(self, cursor):

        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"Sadleirs: Running Stored Procedure to create Publish File...")

        try:

            query = f"Execute SadleirsPublish"
            cursor.execute(query)
            self.conn.commit()

            quiet_batch_process_logger.info(f"Sadleirs: Stored Procedure run finish...")
            return True
            
        except Exception as e:
            print("Sadleirs: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")
            return False
        

    def GetRecordsToPublish(self, cursor):
        output_filename = ''
        if(self.RunStoredProcedureToCreatePublishFile(cursor)):
            query = f"SELECT * FROM SadleirsEventsToUpload"
            cursor.execute(query)

            print([desc[0] for desc in cursor.description])
            columns=[desc[0] for desc in cursor.description]
            
            data = cursor.fetchall()
            data = [[value if value is not None else '' for value in row] for row in data]
            df = pd.DataFrame(data,columns=columns )
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f'Sadliers_Kerry_{timestamp}.csv'
            
            df.to_csv(output_filename, index=False)
        return output_filename
