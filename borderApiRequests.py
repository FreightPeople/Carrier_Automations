import requests


def get_access_token(client_id, client_secret):
    token_url = "https://integrationapi.borderexpress.com.au/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers) 
    

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return response.status_code, response.text
    
def fetch_consignment_details(consignment_number, access_token):
    base_url = 'https://integrationapi.borderexpress.com.au'
    endpoint = f'{base_url}/api/v1/consignments/{consignment_number}'
    print(access_token)
    print(endpoint)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()  # Returns the consignment details
    else:
        return response.status_code, response.text
    
