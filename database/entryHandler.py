import sqlite3
import time
import requests
import json
from datetime import datetime

dbURL = "http://localhost:8003"
gptURL = "http://localhost:8001"
# Connect to the SQLite database
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Initialize an empty list to store the IDs
ids_list = []

def callGPT(prompt):
    print("Start callGPT")
    # Define the URL
    url = gptURL + "/v1/completions"
    # Define the headers
    headers = {
        "Content-Type": "application/json"
    }

    params = {"query": prompt}

    response = requests.get(url, params=params)
    
    print(response.status_code)
    
    # Check if the request was successful
    if response.status_code ==  200:
        
        data = response.json()
        content = data.get("response")
        sourcesList = data.get("sourcesList")
    
    else:
        print("Request failed with status code:", response.status_code)
    print(sourcesList)
    return content, sourcesList

while True:
    # Query the database for entries where flagA is 0
    cursor.execute("SELECT id FROM chatHistory_en WHERE flagA = 0")
    entries = cursor.fetchall()
    
    # Clear the current list of IDs
    #ids_list.clear()
    if entries:
        # Add the IDs from the query entries to the list
        for row in entries:
            # Make an API call to the queue system
            id = row[0]
            url = dbURL + "/get_prompt"
            headers = {"Content-Type": "application/json"}
            data = {"id": id}
            print(id)
            print(type(id))
            response = requests.get(url, headers=headers, json=data)
            response_data = response.json()
            promptInput = response_data.get("prompt")
            print(promptInput)
            print(type(promptInput))
            gptResult, gptSource = callGPT(promptInput)
            print(gptResult)
            print(gptSource)
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            updateData = {
                    "id": id,
                    "response": gptResult,
                    "source1": gptSource[0],
                    "source2": gptSource[1],
                    "flagA": 1,
            }
            
            response = requests.post(dbURL + "/update_entry", json=updateData)
            response_data = response.json()
            print(response_data)
    
    # Print the list of IDs for demonstration purposes
    if entries:
        print("Current IDs with flagA = False:", entries)
    else:
        print("No ID with flagA = 0")
    
    # Sleep for a while before the next query to avoid overloading the database
    time.sleep(5) # Adjust the sleep duration as needed
