import requests
import json

query = {"query": "What is the weather like in New York City today?"}
url = "http://127.0.0.1:8080/invoke"
data = json.dumps(query)

print("data: ", data)
response = requests.post(url, data)

print("status:", response.status_code)
print("response:", response.json())

