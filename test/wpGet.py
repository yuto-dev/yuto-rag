import requests
import base64

def get_last_insert_id():
    url = "https://kayumeranti.my.id/wp-json/chat/v1/last-insert-id"
    user = 'abi'
    password = 'LipP JZPt hArJ ieLl 5g0G bpDr'

    try:
        
        wp_connection = user + ':' + password
        token = base64.b64encode(wp_connection.encode())

        headers = {
        "Content-Type": "application/json",
        "Authorization": 'Basic ' + token.decode('utf-8')
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes
        data = response.json()
        return data.get('last_insert_id', None)
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

# Example usage
last_insert_id = get_last_insert_id()
if last_insert_id is not None:
    print("Last inserted ID:", last_insert_id)
else:
    print("Failed to retrieve last inserted ID.")
