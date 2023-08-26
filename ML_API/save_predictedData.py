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

# Fetch predicted power from testing table
query_testing = "SELECT `Date/Time`, `predicted power` FROM testing WHERE DATE(`Date/Time`) = '2022-12-02'"
cursor.execute(query_testing)
predicted_power = cursor.fetchall()

# Update energy_data table with predicted power
query = "UPDATE energy_data SET `predicted power` = %s WHERE `Date/Time` = %s"
values = [(entry[1], entry[0]) for entry in predicted_power]

# Execute the update query for each row
cursor.executemany(query, values)

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()