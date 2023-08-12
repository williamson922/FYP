import mysql.connector
from datetime import datetime

# Connect to the database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "energyctrl"
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Read the file data
with open('dataset-with-timestamp.csv', 'r') as file:
    data = file.read()

# Assuming you have read data from the file
data_lines = data.split('\n')
values_to_insert = []

# Execute SQL query to insert data
query = "INSERT INTO energy_data (`Date/Time`,`Voltage Ph-A Avg`,`Voltage Ph-B Avg`,`Voltage Ph-C Avg`, `Current Ph-A Avg`, `Current Ph-B Avg`, `Current Ph-C Avg`,`Power Factor Total`, `Power Ph-A`, `Power Ph-B`, `Power Ph-C`, `Total Power`, `Unix Timestamp`) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s)"

# Skip the header line
header_skipped = False

for line in data_lines:
    if not header_skipped:
        header_skipped = True
        continue  # Skip the header line
        
    values = line.split(',')
    if len(values) > 0 and any(value.strip() for value in values):
        values[0] = datetime.strptime(values[0], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(query, values)  # Execute the query for each row


# Commit changes and close connections
conn.commit()
cursor.close()
conn.close()