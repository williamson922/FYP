import pandas as pd
from datetime import datetime
import os

# Read the text file
with open('E18CT03058_LP2.txt', 'r') as file:
    lines = file.readlines()

# Initialize variables
current_year = None
current_month = None
current_day = None
data = []
current_date = None  # Keep track of the current date

# Iterate through lines in the text file
for line in lines[1:]:  # Skip the header row
    # Split the line into columns
    columns = line.strip().split('\t')

    # Parse the date/time column
    date_str = columns[0]
    date = datetime.strptime(date_str, '%d/%m/%Y %I:%M:%S %p')

    # Check if it's a new year
    if date.year != current_year:
        # Create a new folder for the new year
        current_year = date.year
        os.makedirs(str(current_year), exist_ok=True)

    # Check if it's a new month
    if date.month != current_month:
        # Create a new folder for the new month
        current_month = date.month
        month_folder = date.strftime('%m-%Y')
        os.makedirs(f'{current_year}/{month_folder}', exist_ok=True)

    # Check if it's a new day
    if date.day != current_day:
        # Create a new DataFrame for the new day
        if data:
            day_df = pd.DataFrame(data)
            day_df.columns = lines[0].strip().split('\t')
            day_folder = current_date.strftime('%d-%m-%Y')  # Use the recorded date
            day_df.to_csv(f'{current_year}/{month_folder}/{day_folder}.csv', index=False)

        # Update current_date and current_day
        current_date = date.date()
        current_day = date.day
        data = []

    # Append the line to the data for the current day
    data.append(columns)

# Create a CSV file for the last day
if data:
    day_df = pd.DataFrame(data)
    day_df.columns = lines[0].strip().split('\t')
    day_folder = current_date.strftime('%d-%m-%Y')
    day_df.to_csv(f'{current_year}/{month_folder}/{day_folder}.csv', index=False)
