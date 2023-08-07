import requests
import json
import numpy as np
import traceback
import logging

def get_user_input():
    data = {}
    
    print("Please enter the data:")
    data['Date/Time'] = input("Date/Time: ")
    data['Voltage Ph-A Avg'] = float(input("Voltage Ph-A Avg: "))
    data['Voltage Ph-B Avg'] = float(input("Voltage Ph-B Avg: "))
    data['Voltage Ph-C Avg'] = float(input("Voltage Ph-C Avg: "))
    data['Current Ph-A Avg'] = float(input("Current Ph-A Avg: "))
    data['Current Ph-B Avg'] = float(input("Current Ph-B Avg: "))
    data['Current Ph-C Avg'] = float(input("Current Ph-C Avg: "))
    data['Power Factor Total'] = float(input("Power Factor Total: "))
    # Add more keys as needed based on your API endpoint's requirements
    
    return data

def simulate_outside_system():
    # Replace 'http://localhost:your_port/api/endpoint' with the actual URL of your web application's API endpoint.
    url = 'http://localhost:8000/api/bms-data'
    
    data = get_user_input()
    print(data)
    try:
        response = requests.post(url, json=[data])  # Use requests.post for POST requests
        if response.status_code == 200:
            print('Response from the web application:')
            print(response)  # Assuming the response is in JSON format
        else:
            print(f'Request failed with status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        # Log the full traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        print('Error while sending the request:', str(e))

if __name__ == "__main__":
    simulate_outside_system()