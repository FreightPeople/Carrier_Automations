import time 
import pymssql
from configparser import ConfigParser
from carriers.tnt import Tnt
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import csv
import ftplib
import requests
from datetime import datetime
import re
# Read database configuration from config.ini
import os

def initiateTntETAUpdate(cursor, conn):
    # Establish the database connection
    # Import the Tfm class from carriers/tfm.py
    cario_auth_token = get_cario_token()
    tnt = Tnt(cursor,conn)
    selenium_tnt = tnt.login()
    records = tnt.retreive_records(cursor)
    if records and len(records) > 0:
        for record in records:
            consignment_number = record[0]  # Assuming consignment number is at index 1
            print(f"Processing record {record[0]} with cario ETA of {record[1]}...")
            eta = tnt.get_web_ETA(selenium_tnt, record[0], record[2])  
            #today_date = datetime.now().date()
            if eta[1] is not None:  
                #if(datetime.strptime(eta[1], "%d/%m/%Y %H:%M").date() != today_date) 
                update_cario_eta(eta,cario_auth_token)
    time.sleep(2)

        

def update_cario_eta(record,cario_auth_token):
    # Implement the code to update the cario ETA in the database
    url = "https://entities.cario.com.au/api/Consignment/UpdateETA"

    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cario_auth_token}"
    }
    match = re.search(r'\d+/\d+/\d+\s+\d+:\d+', record[1])
    if match:
        eta_datetime_str = match.group(0)
    else:
        print("ETA string does not contain a valid date and time format.")
    # Handle this case accordingly

    # Parse the extracted date and time string into a datetime object
    eta_datetime = datetime.strptime(eta_datetime_str, "%d/%m/%Y %H:%M")
    eta_date_only_str = eta_datetime.strftime("%m/%d/%Y")
    print(f"id - {record[2]}")
    print(eta_date_only_str)
    payload = {
        "consignmentId": record[2],  # Replace 123 with the actual consignment ID
        "eta": eta_date_only_str,  # Replace with the desired ETA string
        "reason": 'updated ETA based on website'  # Replace with the reason for the update   
    }
  
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        #result = response.json()
        print(f"ETA update for consignment {record[1]} was successful.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating ETA for consignment {record[1]}: {e}")



def get_cario_token():
    CarioAuthUrl = "https://entities.cario.com.au/api/TokenAuth/Authenticate"

    # Headers
    headers = {
        "accept": "text/plain",
        "Content-Type": "application/json-patch+json",
        #"Abp.TenantId": "43"
    }

    # Body with credentials (replace variables with actual values)
    body = {
        "userNameOrEmailAddress": os.environ['CARIO_USERNAME'],  # Replace with actual username
        "password": os.environ['CARIO_PASSWORD'],  # Replace with actual password
        "rememberClient": False
    }
    try:
        # Making the POST request
        response = requests.post(CarioAuthUrl, headers=headers, json=body)
        response.raise_for_status()  # Raises an exception for 4XX or 5XX status codes

        # Extracting the access token from the response
        carioAuthToken = response.json().get('result', {}).get('accessToken', '')
        return carioAuthToken

    except requests.RequestException as e:
        print("Error:", e) 
    

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