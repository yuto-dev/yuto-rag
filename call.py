import requests

url = "http://127.0.0.1:8001/v1/completions"  # Replace this with your actual endpoint URL
query = "What changes do I need in my personality to make friends easily?"  # Replace this with your query

params = {"query": query}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    answer = data.get("response")
    result_list = data.get("sourcesList")
    print("Answer:", answer)
    print("Result List:", result_list)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
