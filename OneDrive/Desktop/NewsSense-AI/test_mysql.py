from src.mysql_database import get_connection

conn = get_connection()

if conn:
    print("MySQL connected successfully")
    conn.close()
else:
    print("MySQL connection failed")