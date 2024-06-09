import requests
import json
import base64
from datetime import datetime
import time

url = "https://kayumeranti.my.id/wp-json/chat/v1/insert"
user = 'abi'
password = 'LipP JZPt hArJ ieLl 5g0G bpDr'

# Get the current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

data = {
    "prompt": "What's the best restaurant?",
    "response": "I don't know.",
    "sourceA": "User",
    "sourceB": "AI",
    "flagA": 0,
    "flagB": 1,
    "chatID": 12345,
    "endTime": current_time  # Add endTime to the data dictionary with the current time
}

data = {
    "prompt": "What's the worst restaurant?",
    "flagA": 0,
    "flagB": 0,
    "chatID": 12345,
}


wp_connection = user + ':' + password
token = base64.b64encode(wp_connection.encode())

headers = {
    "Content-Type": "application/json",
    "Authorization": 'Basic ' + token.decode('utf-8')
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    print("Data inserted successfully.")
else:
    print(f"Error: {response.status_code} - {response.text}")
