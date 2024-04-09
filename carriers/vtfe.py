from agents.selenium_border import SeleniumBorder  
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import os

class Border:

   
    def __init__(self, cursor, conn):
        
        self.conn = conn
        self.cursor = cursor
       

    url = os.environ['VTFE_Base_URL'] 

    def retrieve_records(self, cursor):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"VTFE: Retrieving recordsfrom DB...")

        try:
            query = f"Select [CarrierName], [ConnoteNumber] ,[DeliveryCompany] ,[TimeslotDate] ,[TimeslotTime] ,[IsHazardous] FROM [dbo].[tmp_VTFETimeslots]"
            cursor.execute(query)
            #records = [record[1] for record in cursor.fetchall()]
            records = [(record[1]) for record in cursor.fetchall()]

            quiet_batch_process_logger.info(f"VTFE: Records Retrieved...")

            return records
        
        except Exception as e:
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")


        

    def count_if_records_exists(self, cursor):
        # Count number of records that exist in database
        
        quiet_batch_process_logger.info(f"VTFE: Checking if records exist for search purpose...")

        try:
            query = f"Select COUNT([ConnoteNumber]) FROM [dbo].[tmp_VTFETimeslots]"
            cursor.execute(query)
            records = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"VTFE: Existing Records Counted...")
            return records

        except Exception as e:
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")


        
    def run_stored_procedure(self, cursor):
        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"VTFE: Running Stored Procedure to find more records...")

        try:

            query = f"Execute VTFETimeslotConsignments"
            cursor.execute(query)
            self.conn.commit()

            quiet_batch_process_logger.info(f"VTFE: Stored Procedure run finish...")
            
        except Exception as e:
            print("VTFE: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")



    def save_record(self, cursor, connote, date_text, time_text):
        try:

            
            count_query = f"SELECT COUNT([ConnoteNumber]) from [dbo].[tmp_VTFETimeslots] WHERE [TimeslotTime] = '' and [TimeslotDate] = '' and ConnoteNumber LIKE '{connote}'"
            print("VTFE: Count Query:", count_query)

            cursor.execute(count_query)
            count = cursor.fetchone()[0]

            quiet_batch_process_logger.info(f"VTFE: Count of available connote (check flag if connote already exists): {count}")


            if(count>0):

                update_query = f"Update [dbo].[tmp_VTFETimeslots] SET [TimeslotTime] = '{time_text}', [TimeslotDate] = '{date_text}' Where [ConnoteNumber] = '{connote}';"
                print("VTFE: Update Query:", update_query)

                cursor.execute(update_query)
                self.conn.commit()  # Commit the transaction to save the changes

                print("VTFE: Update successful.")
                quiet_batch_process_logger.info(f"VTFE: Time slot has for {connote} been has been updated...")


            
        except Exception as e:
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")

            print("VTFE: Error:", e)
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
        
        quiet_batch_process_logger.info(f"VTFE: Deleting recordsfrom DB...")
        print('VTFE: Deleting recordsfrom DB...')

        try:
            query = f"DELETE FROM [dbo].[tmp_VTFETimeslots]"
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(e)
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")


    def RunStoredProcedureToCreatePublishFile(self, cursor):

        # Running the stored procedure to fetch the consignments
        quiet_batch_process_logger.error(f"VTFE: Running Stored Procedure to create Publish File...")

        try:

            query = f"Execute VTFETimeslotPublish"
            cursor.execute(query)

            table_result = cursor.fetchall()
            self.conn.commit()
           
            print('commited')
            
            quiet_batch_process_logger.info(f"VTFE: Stored Procedure run finish...")

            return table_result
            
        except Exception as e:
            print("VTFE: Error:", e)
            self.conn.rollback()
            quiet_batch_process_logger.error(f"VTFE: Error : {e}")
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
            output_filename = f'VTFETimeslots_{timestamp}.csv'

            # Save the DataFrame to a CSV file
            df.to_csv(output_filename, index=False)
