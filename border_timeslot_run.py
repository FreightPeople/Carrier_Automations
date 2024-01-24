import time 
from carriers.border import Border
from borderApiRequests import get_access_token, fetch_consignment_details
import pymssql
from configparser import ConfigParser
from datetime import datetime
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

def initiateBorderTimeslots(cursor, conn):

    border = Border(cursor,conn)

    print('Border: ',border.count_if_records_exists(cursor))

    if(border.count_if_records_exists(cursor)==0):
        border.run_stored_procedure(cursor)
        time.sleep(30)
        if(border.count_if_records_exists(cursor)==0):
            exit()
    
    # Retrieve the next record without the date
    records_to_process  = border.retrieve_records(cursor)
    print('Border: ',records_to_process)
    border.delete_records(cursor)
    tempflagcheck = False
    booking_list = []
    try:
        access_token = get_access_token(os.environ['BEX_CLIENT_ID'], os.environ['BEX_CLIENT_SECRET'])
        for record in records_to_process:
            connote, timeslot_date_db, timeslot_time_db = record
            
            consignment_details = fetch_consignment_details(connote, access_token)
            # Check if the response contains the 'TimeslotDate' and 'TimeslotTime'
            if 'TimeslotDate' in consignment_details and 'TimeslotTime' in consignment_details:
                booking_list.append((connote, (consignment_details['TimeslotDate'], consignment_details['TimeslotTime'])))
                print('Added connote and timeslot to booking list: ' + connote + '-' + consignment_details['TimeslotDate'] + '-' + consignment_details['TimeslotTime'])
            else:
                print(f'Timeslot information not available for {connote}')
                                      
        
        csv_data = []
        if(booking_list):
            for barcode, (date_str, time_str) in booking_list:
                
                            # Parse date and time
                timeslot_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                timeslot_time = datetime.strptime(time_str, '%I:%M%p')

                                # Format date and time (remove leading zeros for Windows compatibility)
                formatted_date = timeslot_date.strftime('%m/%d/%Y').lstrip("0").replace("/0", "/")
                formatted_time = timeslot_time.strftime('%H:%M')

                csv_data.append([barcode, formatted_date, formatted_time, "", "BOOKEDIN", "", ""])
                        # Write CSV file
            filename = f"BorderTimeslots_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Barcode', 'Date', 'Time', 'UserID', 'ScanType', 'Location', 'Extra Info'])
                writer.writerows(csv_data)
            upload_file(filename, server, username, password, remote_path)
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    #border.GetRecordsToPublish(cursor)
    
       
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
        initiateBorderTimeslots(cursor,conn)
    except pymssql.DatabaseError as ex:  # Note: changed from pyodbc.Error to pymssql.DatabaseError
        print(f"Error establishing connection: {ex}")
    finally:
        if conn:
            conn.close()    
