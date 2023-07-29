import requests
import json

# JSON data to send to the API
data = {
    "data": [
        {
            "data": [
                {
                    "Date/Time": "12/26/2021 00:00 AM",
                    "Voltage Ph-A Avg": 249.28,
                    "Voltage Ph-B Avg": 250.81,
                    "Voltage Ph-C Avg": 248.03,
                    "Current Ph-A Avg": 7.89,
                    "Current Ph-B Avg": 4.23,
                    "Current Ph-C Avg": 8.86,
                    "Power Factor Total": 0.97
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
