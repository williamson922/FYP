import requests
import traceback
from datetime import datetime

def get_user_input(data_row):
    data = {}
    
    print("Please review the data:")
    data['Date/Time'] = data_row[0]
    data['Voltage Ph-A Avg'] = float(data_row[1].split()[0])
    data['Voltage Ph-B Avg'] = float(data_row[2].split()[0])
    data['Voltage Ph-C Avg'] = float(data_row[3].split()[0])
    data['Current Ph-A Avg'] = float(data_row[4].split()[0])
    data['Current Ph-B Avg'] = float(data_row[5].split()[0])
    data['Current Ph-C Avg'] = float(data_row[6].split()[0])
    data['Power Factor Total'] = float(data_row[7].split()[0])
    # Add more keys as needed based on your API endpoint's requirements
    
    print("\nReview the data:")
    for key, value in data.items():
        print(f"{key}: {value}")
    
    user_input = input("\nDo you confirm this data should be sent to the web? (Y/N): ")
    if user_input.lower() == "y":
        return data
    else:
        return None

def process_data_line(line):
    data_elements = line.split('\t')
    if len(data_elements) != 8:
        return None
    return [element.strip() for element in data_elements]

def simulate_outside_system(start_date):

    url = 'http://localhost:8000/api/bms-data'
    
    with open('testingData.txt', 'r') as file:
        data_lines = file.readlines()

    for line in data_lines[1:]:  # Skipping the header line
        data_row = process_data_line(line)
        if data_row is not None:
            data_date_str = data_row[0].split()[0]  # Extract the date part
            data_date = datetime.strptime(data_date_str, "%d/%m/%Y")  # Correct format here
            if data_date >= start_date:
                data = get_user_input(data_row)
                if data is not None:
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
                print("")  # Add a blank line for readability

if __name__ == "__main__":
    start_date_str = input("Enter the starting date (DD/MM/YYYY): ")  # Corrected the prompt format
    start_date = datetime.strptime(start_date_str, "%d/%m/%Y")  # Corrected the format here
    simulate_outside_system(start_date)
