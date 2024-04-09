import time 
from carriers.vtfe import vtfe
import pymssql
from configparser import ConfigParser
from datetime import datetime
from VTFE_api_calls import fetch_consignment_details
import pandas as pd
from automation_logger import quiet_batch_process_logger
import csv
import ftplib
from datetime import datetime
# Read database configuration from config.ini
import os

FMSconnection_string = (
    f"DRIVER=SQL Server;"
    f"SERVER={os.environ['FMS_SERVER']};"
    f"DATABASE={os.environ['FMS_DATABASE']};"
    f"UID={os.environ['FMS_USERNAME']};"
    f"PWD={os.environ['FMS_PASSWORD']};"
)

server = os.environ['FTP_SERVER']
username = os.environ['FTP_USERNAME']
password = os.environ['FTP_PASSWORD']
remote_path = os.environ['FTP_REMOTE_PATH']


def initiateVTFETimeslots(cursor, conn):
    
        vtfe = vtfe(cursor,conn)
    
        print('VTFE: ',vtfe.count_if_records_exists(cursor))
    
        if(vtfe.count_if_records_exists(cursor)==0):
            vtfe.run_stored_procedure(cursor)
            time.sleep(30)
            if(vtfe.count_if_records_exists(cursor)==0):
                exit()
        
        # Retrieve the next record without the date
        records_to_process  = vtfe.retrieve_records(cursor)
        print('VTFE: ',records_to_process)
        vtfe.delete_records(cursor)
        tempflagcheck = False
        booking_list = []
        try:
            for record in records_to_process:
                connote = record
                
                consignment_details = fetch_consignment_details(connote, os.environ['VTFE_client_id'], os.environ['VTFE_client_secret'])
                # Check if the response contains the 'TimeslotDate' and 'TimeslotTime'
                
                if 'ConsignmentBookingDateTime' in consignment_details:
                    if(consignment_details['ConsignmentBookingDateTime'] is not None or consignment_details['ConsignmentBookingDateTime'] != ''):
                        booking_list.append((connote, (consignment_details['ConsignmentBookingDateTime'])))
                        print('Added connote and timeslot to booking list: ' + connote + '-' + consignment_details['ConsignmentBookingDateTime'])
                    else:
                        print(f'Timeslot information not available for {connote}')
                else:
                    print(f'Timeslot information not available for {connote}')
            csv_data = []
            if booking_list:
                for barcode, booking_datetime in booking_list:
                    # Parse datetime string
                    booking_datetime = datetime.strptime(booking_datetime, '%Y-%m-%d %H:%M')

                    # Format date and time (remove leading zeros for Windows compatibility)
                    formatted_date = booking_datetime.strftime('%m/%d/%Y').lstrip("0").replace("/0", "/")
                    formatted_time = booking_datetime.strftime('%H:%M')

                    csv_data.append([barcode, formatted_date, formatted_time, "", "BOOKEDIN", "", ""])

                # Write CSV file
                filename = f"VTFETimeslots_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Barcode', 'Date', 'Time', 'UserID', 'ScanType', 'Location', 'Extra Info'])
                    writer.writerows(csv_data)

                upload_file(filename, server, username, password, remote_path)
        except:
            print('Error fetching consignment details')


    
    
       
def upload_file(file_name, server, username, password, remote_path):
    try:
        with ftplib.FTP(server) as ftp:
            ftp.login(username, password)
            ftp.cwd(remote_path)

            with open(file_name, 'rb') as file:
                # Upload file
                response = ftp.storbinary(f'STOR {file_name}', file)
                print("Upload response:", response)

            # Verify if file is uploaded
            if file_name in ftp.nlst():
                print(f"{file_name} has been successfully uploaded.")
            else:
                print(f"Failed to upload {file_name}.")
    except ftplib.all_errors as e:
        print("FTP error:", e)

if __name__ == "__main__":
    # Establish the database connection
    try:
        conn = pymssql.connect(
            server=os.environ['FMS_SERVER'],
            user=os.environ['FMS_USERNAME'],
            password=os.environ['FMS_PASSWORD'],
            database=os.environ['FMS_DATABASE']
        )
        print("Connection established successfully.")
        cursor = conn.cursor()
        (cursor,conn)
    except pymssql.DatabaseError as ex:  # Note: changed from pyodbc.Error to pymssql.DatabaseError
        print(f"Error establishing connection: {ex}")
    finally:
        if conn:
            conn.close()    
