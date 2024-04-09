import requests

def fetch_consignment_details(consignment_number,client_id,client_secret):
    url = 'https://api.transvirtual.com.au/Api/ConsignmentQuery'
    headers = {
        # has to be in format client_id|client_secret
        'Authorization': f'{client_id}|{client_secret}',
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    data = {
        "ConsignmentNumber": consignment_number
    }

    response = requests.post(url, headers=headers, json=data)
    #print(response.json())
    return response.json()