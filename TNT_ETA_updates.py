import time 
import pymssql
from configparser import ConfigParser
from carriers.tnt import Tnt
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import csv
import ftplib
from datetime import datetime
# Read database configuration from config.ini
import os

def initiateTntETAUpdate(cursor, conn):
    # Establish the database connection
    # Import the Tfm class from carriers/tfm.py
    
    tnt = Tnt(cursor,conn)
    selenium_tnt = tnt.login()
    records = tnt.retreive_records(cursor)
    if records and len(records) > 0:
        for record in records:
            eta = tnt.get_web_ETA(selenium_tnt, record[1])
            print(f"ETA for {record[1]} is {eta}")
    time.sleep(2)
    # Import the SeleniumTnt class from agents

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
        initiateTntETAUpdate(cursor, conn)

    except pymssql.DatabaseError as ex:  # Note: changed from pyodbc.Error to pymssql.DatabaseError
        print(f"Error establishing connection: {ex}")
    finally:
        if conn:
            conn.close()