import time 
import pymssql
from configparser import ConfigParser
from carriers.toll import Toll
from toll_api_call import toll_api_call
from cario_api_calls import cario_api_calls
from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import csv
import ftplib
import requests
from datetime import datetime
import json
import re
import base64
# Read database configuration from config.ini
import os


def get_toll_cons(cursor,conn):
    carrier_to_business_id = {
        4: "IPEC",
        5: "IntermodalSpecialised",
        6: "PriorityAustralia",  # or "PriorityNewZealand", choose one or both
        7: "Tasmania",
        22: "IntermodalSpecialised",
        84: "IPEC",
        166: "Courier"
    }
    toll = Toll(cursor,conn)
    records = toll.retreive_cons_without_eta()
    cario_call = cario_api_calls()
    if records:
        for consignment_number, carrier_id, consignment_id in records:
            print(f"Processing record {consignment_number}")
            # Check if the carrier ID is mapped to a Toll Identifier
            business_id = carrier_to_business_id.get(carrier_id)
            if business_id:
                toll_call = toll_api_call()  
                eta = toll_call.get_toll_eta(consignment_number, business_id)
                eta_date = datetime.strptime(eta, "%d/%m/%Y")
                # Convert the datetime object to "mm/dd/yyyy" format
                eta_date_mm_dd_yyyy = eta_date.strftime("%m/%d/%Y")
                if eta is not None:
                    print(f"ETA for consignment {consignment_number} is {eta}") 
                    cario_call.update_cario_eta(consignment_id, eta_date_mm_dd_yyyy)
                
            else:
                print("No Toll Identifier found for this carrier:", carrier_id)
            


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
        get_toll_cons(cursor, conn)
    except pymssql.DatabaseError as ex:  # Note: changed from pyodbc.Error to pymssql.DatabaseError
        print(f"Error establishing connection: {ex}")
    finally:
        if conn:
            conn.close()