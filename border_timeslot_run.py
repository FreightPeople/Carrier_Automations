import time 
from carriers.border import Border
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

    tempflagcheck = False
    booking_list = []
    selenium_border = border.login()
    try:
        for connote in records_to_process:
            print('Border: Processing : ', connote)
            if connote:
                
                quiet_batch_process_logger.info(f"Border: Starting process for Con : {connote}")
                datetimeval  = border.process_record(selenium_border,connote)
                
                if datetimeval is not None and all(val not in (None, '') for val in datetimeval):
                    #border.save_record(cursor, connote, datetimeval[0], datetimeval[1])
                    #print('Border: ',connote)
                    #print('Border Date: ',datetimeval[0])
                    #print('Border Time: ',datetimeval[1])
                    booking_list.append((connote,(datetimeval[0],datetimeval[1])))
                    print('Added connote and timeslot to booking list' + connote + '-' + datetimeval[0] + '-' + datetimeval[1])
        #border.close_browser(selenium_border)
        csv_data = []
        if(booking_list):
            for barcode, (date_str, time_str) in booking_list:
                
                            # Parse date and time
                timeslot_date = datetime.strptime(date_str, '%d/%m/%Y')
                timeslot_time = datetime.strptime(time_str, '%I:%M %p')

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
        border.delete_records(cursor)
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
    conn = pyodbc.connect(FMSconnection_string)
    cursor = conn.cursor()
    initiateBorderTimeslots(cursor,conn)
    conn.close()