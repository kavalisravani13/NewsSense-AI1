from src.mysql_database import get_connection

connection = get_connection()

if connection:
    print("Connection test passed")
    connection.close()