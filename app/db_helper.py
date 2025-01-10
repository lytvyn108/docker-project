# db_helper.py
import mysql.connector

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(
        host="db",  # Service name in docker-compose.yml
        user="user",  # MySQL username
        password="password",  # MySQL password
        database="mydb"  # Your database name
    )

# Insert a customer into the database
def insert_customer(customer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Customer (firstname, surname, email) VALUES (%s, %s, %s)",
        (customer["firstname"], customer["surname"], customer["email"])
    )
    conn.commit()
    conn.close()

# Insert a wine into the database
def insert_wine(wine):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Wine (name, type, price, country, alcoholPercentage) VALUES (%s, %s, %s, %s, %s)",
        (wine["name"], wine["type"], wine["price"], wine["country"], wine["alcoholPercentage"])
    )
    conn.commit()
    conn.close()

# Fetch all wines from the database
def fetch_all_wines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Returns rows as dictionaries
    cursor.execute("SELECT * FROM Wine;")
    wines = cursor.fetchall()
    conn.close()
    return wines
