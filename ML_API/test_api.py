import requests
import json

# JSON data to send to the API
data = {
    "data": [
        {
            "data": [
                {
                   "Date/Time": "12/22/2021 00:00 AM",
                    "Voltage Ph-A Avg": 246.91,
                    "Voltage Ph-B Avg": 248.37,
                    "Voltage Ph-C Avg": 246.88,
                    "Current Ph-A Avg": 7.47,
                    "Current Ph-B Avg": 4.44,
                    "Current Ph-C Avg": 4.53,
                    "Power Factor Total": 1
                }
            ]
        }
    ]
}

# API endpoint URL
url = "http://localhost:5000/api/predict"

# Headers for the HTTP request
headers = {
    "Content-Type": "application/json"
}

# Send the POST request to the API
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response from the API
print(response.json())
