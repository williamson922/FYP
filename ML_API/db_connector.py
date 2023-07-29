import mysql.connector

def get_database_connection():
    # Replace these values with your MySQL database credentials
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'energyctrl',
    }

    # Connect to the database
    connection = mysql.connector.connect(**db_config)

    return connection


