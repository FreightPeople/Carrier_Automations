import time 
from carriers.tfm import Tfm
import pyodbc
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
    
def initiateTfmTimeslots(cursor, conn):
    # Establish the database connection
    
    tfm = Tfm(cursor,conn)
    selenium_tfm = tfm.login()
    if(tfm.count_if_records_exists(cursor)==0):
        print('TFM: ',tfm.count_if_records_exists(cursor))
        tfm.run_stored_procedure(cursor)
        time.sleep(10)
        if(tfm.count_if_records_exists(cursor)==0):
            exit()
    records_to_process = tfm.retrieve_records(cursor)
    booking_list = []
    for connote in records_to_process:
        print('TFM: Processing : ', connote)
        if connote:
            booking_details = tfm.process_timeslots(selenium_tfm,connote)
            print('TFM: ',connote , booking_details)
            if(booking_details is not None):
                booking_list.append((connote,booking_details))
    tfm.close_browser(selenium_tfm)
    tfm.delete_records(cursor) 
    csv_data = []
    if(booking_list):
        for barcode, times in booking_list:
            for date_str, time_str in times:
            # Parse date and time
                timeslot_date = datetime.strptime(date_str, '%d/%m/%Y')
                timeslot_time = datetime.strptime(time_str, '%I:%M %p')

                # Format date and time (remove leading zeros for Windows compatibility)
                formatted_date = timeslot_date.strftime('%m/%d/%Y').lstrip("0").replace("/0", "/")
                formatted_time = timeslot_time.strftime('%H:%M')

                csv_data.append([barcode, formatted_date, formatted_time, "", "BOOKEDIN", "", ""])
        # Write CSV file
        filename = f"TFMTimeslot_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Barcode', 'Date', 'Time', 'UserID', 'ScanType', 'Location', 'Extra Info'])
            writer.writerows(csv_data)
    # Upload CSV file
        upload_file(filename, server, username, password, remote_path)
    #tfm.close_browser(selenium_Tfm)
    
    
    
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
    conn = pyodbc.connect(FMSconnection_string)
    cursor = conn.cursor()
    initiateTfmTimeslots(cursor, conn)
    conn.close()

    