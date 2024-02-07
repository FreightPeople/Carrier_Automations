from agents.selenium_border import SeleniumBorder  
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import os

class Border:

   
    def __init__(self, cursor, conn):
        
        self.conn = conn
        self.cursor = cursor
       

    url = os.environ['BEX_LOGIN_URL']  # Update with your URL

    def retrieve_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"Border: Retrieving recordsfrom DB...")

        try:
            query = f"Select [CarrierName], [ConnoteNumber] ,[DeliveryCompany] ,[TimeslotDate] ,[TimeslotTime] ,[IsHazardous] FROM [dbo].[tmp_BorderTimeslots]"
            cursor.execute(query)
            #records = [record[1] for record in cursor.fetchall()]
            records = [(record[1]) for record in cursor.fetchall()]

            quiet_batch_process_logger.info(f"Border: Records Retrieved...")

            return records
        
        except Exception as e:
            quiet_batch_process_logger.error(f"Border: Error : {e}")

    def add_record_to_db(self, cursor, consignment_data):
        consignment_number, consignment_date = consignment_data
        # Check if consignment already exists
        query =f"SELECT COUNT(*) FROM [dbo].[BorderDeliveryDates] WHERE [Consignment Number] = '{consignment_number}'"

        cursor.execute(query)
        
        count = cursor.fetchone()[0]
        #print(f"Border: Found {count} records for consignment {consignment_number}")

        # If not found, insert the new consignment
        if count == 0:
            query2 =f"INSERT INTO [dbo].[BorderDeliveryDates] ([Consignment Number], [Date Signed]) VALUES ('{consignment_number}', '{consignment_date}')"
            cursor.execute(query2)
            self.conn.commit()  # Commit the transaction to save the changes
            #print(f"Border: Added consignment {consignment_number} to database")
            return True
        return False  # Indicates that a consignment was not added


        

    def count_if_records_exists(self, cursor):
        # Count number of records that exist in database
        
        quiet_batch_process_logger.info(f"Border: Checking if records exist for search purpose...")

        try:
            query = f"Select COUNT([ConnoteNumber]) FROM [dbo].[tmp_BorderTimeslots]"
            cursor.execute(query)
            records = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"Border: Existing Records Counted...")
            return records

        except Exception as e:
            quiet_batch_process_logger.error(f"Border: Error : {e}")


        
    def run_stored_procedure(self, cursor):
        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"Border: Running Stored Procedure to find more records...")

        try:

            query = f"Execute BorderTimeslotConsignments"
            cursor.execute(query)
            self.conn.commit()

            quiet_batch_process_logger.info(f"Border: Stored Procedure run finish...")
            
        except Exception as e:
            print("Border: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Border: Error : {e}")



    def login(self):
         # Initialize your SeleniumBorder class with the connote value
        selenium_border = SeleniumBorder(self.url, quiet_batch_process_logger)
        selenium_border.open_website()
        selenium_border.login()
        return selenium_border
    
    def process_history(self, selenium_border):
        consignments = selenium_border.fetch_connotes_from_history()
        quiet_batch_process_logger.info(f"Border: History Processed...")
        return consignments

    def process_record(self, selenium_border ,connote):
       
        selenium_border.perform_search(connote)
        datetimeval = selenium_border.extract_details(connote)
        quiet_batch_process_logger.info(f"Border: Record Processed for Connote : {connote}")

        return datetimeval
    
    def close_browser(self, selenium_border):
        
        selenium_border.close_browser()


    def save_record(self, cursor, connote, date_text, time_text):
        try:

            
            count_query = f"SELECT COUNT([ConnoteNumber]) from [dbo].[tmp_BorderTimeslots] WHERE [TimeslotTime] = '' and [TimeslotDate] = '' and ConnoteNumber LIKE '{connote}'"
            print("Border: Count Query:", count_query)

            cursor.execute(count_query)
            count = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"Border: Count of available connote (check flag if connote already exists): {count}")


            if(count>0):

                update_query = f"Update [dbo].[tmp_BorderTimeslots] SET [TimeslotTime] = '{time_text}', [TimeslotDate] = '{date_text}' Where [ConnoteNumber] = '{connote}';"
                print("Border: Update Query:", update_query)

                cursor.execute(update_query)
                self.conn.commit()  # Commit the transaction to save the changes

                print("Border: Update successful.")
                quiet_batch_process_logger.info(f"Border: Time slot has for {connote} been has been updated...")


            
        except Exception as e:
            quiet_batch_process_logger.error(f"Border: Error : {e}")

            print("Border: Error:", e)
            self.conn.rollback()

    # DELETE NOT REQUIRED

    # def delete_record(self, cursor, connote):

    #     try:
    #         delete_query = f"DELETE FROM [dbo].[tmp_SadleirsConsignments] WHERE [ConnoteNumber]='{connote}'"
    #         print("Sadleirs: Delete Query:", delete_query)

    #         cursor.execute(delete_query)
    #         self.conn.commit()  # Commit the transaction to save the changes
    #         quiet_batch_process_logger.info(f"Sadleirs: Record for {connote} deleted from temp table...")

    #         print("Sadleirs: Delete successful.")

            
    #     except Exception as e:
    #         print("Sadleirs: Error:", e)
    #         self.conn.rollback()
    #         quiet_batch_process_logger.error(f"Sadleirs: Error : {e}")

    def delete_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"Border: Deleting recordsfrom DB...")
        print('Border: Deleting recordsfrom DB...')

        try:
            query = f"DELETE FROM [dbo].[tmp_BorderTimeslots]"
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(e)
            quiet_batch_process_logger.error(f"Border: Error : {e}")

    def run_stored_procedure_history(self, cursor):
        try:

            query = f"Execute BorderDeliveryDates_Publish"
            cursor.execute(query)
            self.conn.commit()
           
            print('Border History - commited')
            quiet_batch_process_logger.info(f"Border: Stored Procedure run finish...")
            
        except Exception as e:
            print("Border: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Border: Error : {e}")
            return None

    def RunStoredProcedureToCreatePublishFile(self, cursor):

        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"Border: Running Stored Procedure to create Publish File...")

        try:

            query = f"Execute BorderTimeslotPublish"
            cursor.execute(query)

            table_result = cursor.fetchall()
            self.conn.commit()
           
            print('commited')
            
            quiet_batch_process_logger.info(f"Border: Stored Procedure run finish...")

            return table_result
            
        except Exception as e:
            print("Border: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"Border: Error : {e}")
            return None
        

    def GetRecordsToPublish(self, cursor):

        response_table = self.RunStoredProcedureToCreatePublishFile(cursor)

        if(response_table is not None):
           
            # Get the column names from the 'response_table' structure (assuming it has a description attribute)
            columns = [desc[0] for desc in response_table.description]

            # Assuming 'table_result' contains the table data fetched from the SQL query
            data = [[value if value is not None else '' for value in row] for row in response_table]

            # Create a DataFrame from the data and columns
            df = pd.DataFrame(data, columns=columns)

            # Generate a timestamp for the output filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Specify the output filename
            output_filename = f'BorderTimeslots_{timestamp}.csv'

            # Save the DataFrame to a CSV file
            df.to_csv(output_filename, index=False)
