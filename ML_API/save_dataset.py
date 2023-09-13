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