from flask import Flask, jsonify, request, render_template
from random_data_generator import generate_customers, generate_wines, generate_orders, generate_collection_wines, generate_contains, generate_is_paired, generate_reviews  # Import the generator
import mysql.connector
import logging

app = Flask(__name__)

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(
        host="db",  # Service name from docker-compose.yml
        user="user",  # MySQL username as defined in docker-compose.yml
        password="password",  # MySQL password as defined
        database="mydb"  # Your database name
    )

# Home page route
@app.route("/")
def home():
    return render_template("index.html")  # Render the GUI

# Add a new customer
@app.route("/api/customers", methods=["POST"])
def add_customer():
    customer = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customer (firstname, surname, email) VALUES (%s, %s, %s)",
            (customer["firstname"], customer["surname"], customer["email"])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Customer added successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error inserting customer: {e}")
        return jsonify({"error": str(e)}), 500

# Add a new wine
@app.route("/api/wines", methods=["POST"])
def add_wine():
    wine = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Wine (name, type, price, country, alcoholPercentage) VALUES (%s, %s, %s, %s, %s)",
            (wine["name"], wine["type"], wine["price"], wine["country"], wine["alcoholPercentage"])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Wine added successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error inserting wine: {e}")
        return jsonify({"error": str(e)}), 500

# Populate the database with random data
@app.route("/populate-database", methods=["POST"])
def populate_database():
    try:
        num_customers = 10
        num_wines = 10
        num_orders = 5
        num_collection_wines = 3
        num_contains = 5
        num_pairs = 3
        num_reviews = 5
        customers = generate_customers(num_customers)
        wines = generate_wines(num_wines)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete old data
        cursor.execute("DELETE FROM Contains")
        cursor.execute("DELETE FROM IsPaired")
        cursor.execute("DELETE FROM Review")
        cursor.execute("DELETE FROM `Order`")
        cursor.execute("DELETE FROM CollectionWine")
        cursor.execute("DELETE FROM Customer")
        cursor.execute("DELETE FROM Wine")

        # Insert customers
        customer_ids = []
        for customer in customers:
            cursor.execute(
                "INSERT INTO Customer (firstname, surname, email) VALUES (%s, %s, %s)",
                (customer["firstname"], customer["surname"], customer["email"])
            )
            customer_ids.append(cursor.lastrowid)

        # Update customers with their IDs
        for i, customer_id in enumerate(customer_ids):
            customers[i]["customerID"] = customer_id

        # Insert wines
        wine_ids = []
        for wine in wines:
            cursor.execute(
                "INSERT INTO Wine (name, type, price, country, alcoholPercentage) VALUES (%s, %s, %s, %s, %s)",
                (wine["name"], wine["type"], wine["price"], wine["country"], wine["alcoholPercentage"])
            )
            wine_ids.append(cursor.lastrowid)

        # Update wines with their IDs
        for i, wine_id in enumerate(wine_ids):
            wines[i]["wineID"] = wine_id

        # Generate and insert collection wines
        collection_wines = generate_collection_wines(wines, num_collection_wines)
        for collection_wine in collection_wines:
            cursor.execute(
                "INSERT INTO CollectionWine (wineID, numberInCollection, specialPackaging) VALUES (%s, %s, %s)",
                (collection_wine["wineID"], collection_wine["numberInCollection"], collection_wine["specialPackaging"])
            )

        # Generate and insert orders
        orders = generate_orders(customers, num_orders)
        order_ids = []
        for order in orders:
            cursor.execute(
                "INSERT INTO `Order` (customerID, status, deliveryPrice) VALUES (%s, %s, %s)",
                (order["customerID"], order["status"], order["deliveryPrice"])
            )
            order_ids.append(cursor.lastrowid)

        # Update orders with their IDs
        for i, order_id in enumerate(order_ids):
            orders[i]["orderID"] = order_id
        
        # Generate and insert contains
        contains = generate_contains(orders, wines, num_contains)
        for contain in contains:
            cursor.execute(
                "INSERT INTO Contains (orderID, wineID, quantity) VALUES (%s, %s, %s)",
                (contain["orderID"], contain["wineID"], contain["quantity"])
            )

        # Generate and insert is_paired
        is_paired = generate_is_paired(wines, num_pairs)
        for pair in is_paired:
            cursor.execute(
                "INSERT INTO IsPaired (wineID1, wineID2) VALUES (%s, %s)",
                (pair["wineID1"], pair["wineID2"])
            )

        # Generate and insert reviews
        reviews = generate_reviews(customers, wines, num_reviews)
        for review in reviews:
            cursor.execute(
                "INSERT INTO Review (customerID, wineID, rating, comment) VALUES (%s, %s, %s, %s)",
                (review["customerID"], review["wineID"], review["rating"], review["comment"])
            )

        conn.commit()
        conn.close()
        return jsonify({"message": "Database populated successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error populating database: {e}")
        return jsonify({"error": str(e)}), 500

# Get all wines
@app.route("/api/wines", methods=["GET"])
def get_wines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Returns rows as dictionaries
        cursor.execute("SELECT * FROM Wine;")
        wines = cursor.fetchall()
        conn.close()
        return jsonify(wines), 200
    except Exception as e:
        app.logger.error(f"Error fetching wines: {e}")
        return jsonify({"error": str(e)}), 500

# Route to render the shop page (if you need a separate shop page)
@app.route("/shop")
def shop():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Wine;")
        wines = cursor.fetchall()
        conn.close()
        return render_template("shop.html", wines=wines)
    except Exception as e:
        app.logger.error(f"Error rendering shop: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
