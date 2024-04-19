from datetime import datetime
import pandas as pd
from automation_logger import quiet_batch_process_logger
import pymssql
import os

class Toll:
    def __init__(self,cursor,conn):
        self.conn = conn
        self.cursor = cursor

    def retreive_cons_without_eta(self):
        # Implement the code to retrieve the next record without the date from the database
        
        quiet_batch_process_logger.info(f"Toll: Retrieving records from DB...")

        try:
            query = f"EXEC TollConsignmentsWithoutETA"
            self.cursor.execute(query)
            records = [(record[1],record[3],record[5]) for record in self.cursor.fetchall()]
            #quiet_batch_process_logger.info(f"Toll: Records Retrieved...")
            print(records)

            return records
        except Exception as e:
            quiet_batch_process_logger.error(f"Toll: Error : {e}")