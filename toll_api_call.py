import base64
import json
import requests
import datetime
import uuid
import os


class toll_api_call:
    def __init__(self):
        self.username = os.environ['TOLL_API_USER']
        self.password = os.environ['TOLL_API_PASS']


    def get_toll_eta(self,connote,businessid):
        url = "https://api.teamglobalexp.com:6930/gateway/TollMessageTrackAndTraceRestService/1.0/tom/enquireTrackTrace"
        message_identifier = str(uuid.uuid4())
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode(f"{self.username}:{self.password}".encode()).decode()}'
        }
        payload = {
        "TollMessage": {
            "Header": {
            "MessageVersion": "1.0",
            "MessageIdentifier": message_identifier, #unique identifier for each message
            "CreateTimestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), #timestamp of message creation
            "DocumentType": "TrackAndTrace",
            "Environment": "PRD",
            "MessageSender": "CARIO",
            "AsynchronousMessageFlag":"true",
            "SourceSystemCode": "CARIO",
            "MessageReceiver": "TOLL",
            },
            "TrackAndTrace": {
                    "Request": {
                        "SearchTexts": {
                            "SearchText":[
                        {
                            "Value": connote,
                            "BusinessID": businessid
                        }]
                        }
                    }
            }
        }
        }
        
        # Make the API Call
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Handle the Response
        if response.status_code == 200:
            consignment_data = response.json()
            # Check if EstimatedDelivery is present and not empty
            if 'Shipment' in consignment_data['TollMessage']['TrackAndTrace']['Response']['Shipments']:
                shipment = consignment_data['TollMessage']['TrackAndTrace']['Response']['Shipments']['Shipment'][0]
                if 'DatePeriodCollection' in shipment and 'DatePeriod' in shipment['DatePeriodCollection']:
                    estimated_delivery = shipment['DatePeriodCollection']['DatePeriod'][0].get('Date', None)
                    return estimated_delivery
            # Return None if EstimatedDelivery is not found
            return None
        else:
            print("Failed to retrieve consignment data")
            return None