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
import os



SCTconnection_string = (
    f"DRIVER=SQL Server;"
    f"SERVER={os.environ['SCT_SERVER']};"
    f"DATABASE={os.environ['SCT_DATABASE']};"
    f"UID={os.environ['SCT_USERNAME']};"
    f"PWD={os.environ['SCT_PASSWORD']};"
)

server = os.environ['FTP_SERVER']
username = os.environ['FTP_USERNAME']
password = os.environ['FTP_PASSWORD']
remote_path = os.environ['FTP_REMOTE_PATH']


def initiateBorderHistory(cursor, conn):
    border = Border(cursor,conn)
    selenium_border = border.login()
    consignments = border.process_history(selenium_border)
    added_count = 0
    # Assuming consignments_list contains your extracted consignments
    for consignment in consignments:  # Using a copy to avoid modifying the list during iteration
        consignment_number, consignment_date = consignment
        if not consignment_date:
            print(consignment_number + " - date is null or empty!")
            continue 
        if border.add_record_to_db(cursor, consignment):
            added_count += 1
    print(f"Total consignments added: {added_count}")
    border.run_stored_procedure_history(cursor)
    border.close_browser(selenium_border)
    
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
    conn = pyodbc.connect(SCTconnection_string)
    cursor = conn.cursor()
    initiateBorderHistory(cursor,conn)
    conn.close()

    