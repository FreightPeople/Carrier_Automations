import time 
from carriers.sadleris import Sadleirs 
import pymssql
from configparser import ConfigParser
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import csv
import ftplib
from datetime import datetime
# Read database configuration from config.ini
config = ConfigParser()
config.read('config.ini')
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

def initiateSadleirs(cursor,conn):

    sadleirs = Sadleirs(cursor,conn)

    print('Sadleirs: ',sadleirs.count_if_records_exists(cursor))

    if(sadleirs.count_if_records_exists(cursor)==0):
        sadleirs.run_stored_procedure(cursor)
        time.sleep(30)
        if(sadleirs.count_if_records_exists(cursor)==0):
            exit()
    
    # Retrieve the next record without the date
    records_to_process  = sadleirs.retrieve_records(cursor)
    print('Sadleirs 2: ',records_to_process)
    for connote in records_to_process:
        if(connote is None):
            continue
        print('Sadleirs: Processing : ', connote)
        if connote:
            quiet_batch_process_logger.info(f"Sadleirs: Starting process for Con : {connote}")
            statusEvents = sadleirs.process_record(connote)
            
            if(statusEvents is not None):
                sadleirs.save_record(cursor, connote, statusEvents)
                print('Sadleirs: ',connote)
                    
        sadleirs.delete_record(cursor,connote)

    filename = sadleirs.GetRecordsToPublish(cursor)
    upload_file(filename, server, username, password, remote_path)
    
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
        initiateSadleirs(cursor, conn)
    except pymssql.DatabaseError as ex:  # Note: changed from pyodbc.Error to pymssql.DatabaseError
        print(f"Error establishing connection: {ex}")
    finally:
        if conn:
            conn.close()
 

    
