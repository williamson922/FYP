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

# # Connect to the database
# connection = mysql.connector.connect(**db_config)

# # Create a cursor object to execute queries
# cursor = connection.cursor()

# # Sample query to fetch data from a table
# query = "SELECT * FROM your_table_name"
# cursor.execute(query)

# # Fetch all rows of the result
# result = cursor.fetchall()

# # Print the result
# for row in result:
#     print(row)

# # Close the cursor and connection
# cursor.close()
# connection.close()
