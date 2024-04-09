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
    if response.status_code == 200:
        json_data = response.json()
        data_json = json_data.get('Data', {})
            # Return the Data JSON object
        return data_json
    else:
        # If the request fails, print an error message and return None
        print(f"Failed to fetch consignment details. Status code: {response.status_code}")
        return None