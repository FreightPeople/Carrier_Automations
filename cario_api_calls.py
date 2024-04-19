import requests
import os 


class cario_api_calls:
    def __init__(self):
        CarioAuthUrl = "https://entities.cario.com.au/api/TokenAuth/Authenticate"

        # Headers
        headers = {
            "accept": "text/plain",
            "Content-Type": "application/json-patch+json",
            #"Abp.TenantId": "43"
        }

        # Body with credentials 
        body = {
            "userNameOrEmailAddress": os.environ['CARIO_USERNAME'],  
            "password": os.environ['CARIO_PASSWORD'],  
            "rememberClient": False
        }
        try:
            # Making the POST request
            response = requests.post(CarioAuthUrl, headers=headers, json=body)
            response.raise_for_status()  # Raises an exception for 4XX or 5XX status codes

            # Extracting the access token from the response
            carioAuthToken = response.json().get('result', {}).get('accessToken', '')
            self.carioAuthToken = carioAuthToken

        except requests.RequestException as e:
            print("Error:", e) 
    
    def update_cario_eta(self,consignment_id,eta):
    # to update the cario ETA in the database
        url = "https://entities.cario.com.au/api/Consignment/UpdateETA"

        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.carioAuthToken}"
        }
        
        payload = {
            "consignmentId": consignment_id,  
            "eta": eta,  # format mm/dd/yyyy
            "reason": f'ETA on website'  
        }
    
        try:
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            #result = response.json()
            print(f"ETA update for consignment {consignment_id} was successful.")
        except requests.exceptions.RequestException as e:
            print(f"Error updating ETA for consignment {consignment_id}: {e}")

    