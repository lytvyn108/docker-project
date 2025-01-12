from flask import Flask, jsonify, request, render_template
from random_data_generator import (
    generate_customers,
    generate_wines,
    generate_orders,
    generate_collection_wines,
    generate_contains,
    generate_is_paired,
    generate_reviews
)
import mysql.connector
import logging

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="db",           
        user="user",         
        password="password",
        database="mydb"      
    )

@app.route("/")
def home():
    return render_template("index.html")  

@app.route("/top_spender_report.html")
def top_spender_report():
    return render_template("top_spender_report.html")

@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT customerID, firstname, surname FROM Customer")
    customers = cursor.fetchall()
    conn.close()
    return jsonify(customers)

@app.route("/api/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.json
    wine_id = data.get("wineID")
    customer_id = data.get("customerID")

    if not wine_id or not customer_id:
        return jsonify({"message": "Wine ID and Customer ID are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if the wine exists
    cursor.execute("""
        SELECT wineID, name, price
        FROM Wine
        WHERE wineID = %s
    """, (wine_id,))
    wine = cursor.fetchone()

    if not wine:
        conn.close()
        return jsonify({"message": "Wine not found"}), 404

    # Check if the customer has an active order
    cursor.execute("""
        SELECT orderID
        FROM `Order`
        WHERE customerID = %s AND status = 'active'
    """, (customer_id,))
    order = cursor.fetchone()

    if not order:
        # Create a new order if none exists
        cursor.execute("""
            INSERT INTO `Order` (customerID, status, deliveryPrice)
            VALUES (%s, 'active', 0)
        """, (customer_id,))
        order_id = cursor.lastrowid
    else:
        order_id = order["orderID"]

    # Add the wine to the order
    cursor.execute("""
        INSERT INTO Contains (orderID, wineID, quantity)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE quantity = quantity + 1
    """, (order_id, wine_id))

    # Update the order total
    cursor.execute("""
        UPDATE `Order`
        SET deliveryPrice = deliveryPrice + %s
        WHERE orderID = %s
    """, (wine["price"], order_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Wine added to order successfully"}), 200


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

     
        cursor.execute("DELETE FROM Contains")
        cursor.execute("DELETE FROM IsPaired")
        cursor.execute("DELETE FROM Review")
        cursor.execute("DELETE FROM `Order`")
        cursor.execute("DELETE FROM CollectionWine")
        cursor.execute("DELETE FROM Customer")
        cursor.execute("DELETE FROM Wine")

       
        customer_ids = []
        for customer in customers:
            cursor.execute(
                "INSERT INTO Customer (firstname, surname, email) VALUES (%s, %s, %s)",
                (customer["firstname"], customer["surname"], customer["email"])
            )
            customer_ids.append(cursor.lastrowid)

       
        for i, customer_id in enumerate(customer_ids):
            customers[i]["customerID"] = customer_id

       
        wine_ids = []
        for wine in wines:
            cursor.execute(
                "INSERT INTO Wine (name, type, price, country, alcoholPercentage) VALUES (%s, %s, %s, %s, %s)",
                (wine["name"], wine["type"], wine["price"], wine["country"], wine["alcoholPercentage"])
            )
            wine_ids.append(cursor.lastrowid)

     
        for i, wine_id in enumerate(wine_ids):
            wines[i]["wineID"] = wine_id

       
        collection_wines = generate_collection_wines(wines, num_collection_wines)
        for collection_wine in collection_wines:
            cursor.execute(
                "INSERT INTO CollectionWine (wineID, numberInCollection, specialPackaging) VALUES (%s, %s, %s)",
                (
                    collection_wine["wineID"],
                    collection_wine["numberInCollection"],
                    collection_wine["specialPackaging"]
                )
            )

       
        orders = generate_orders(customers, num_orders)
        order_ids = []
        for order in orders:
            cursor.execute(
                "INSERT INTO `Order` (customerID, status, deliveryPrice) VALUES (%s, %s, %s)",
                (order["customerID"], order["status"], order["deliveryPrice"])
            )
            order_ids.append(cursor.lastrowid)

       
        for i, order_id in enumerate(order_ids):
            orders[i]["orderID"] = order_id

        
        contains = generate_contains(orders, wines, num_contains)
        for contain in contains:
            cursor.execute(
                "INSERT INTO Contains (orderID, wineID, quantity) VALUES (%s, %s, %s)",
                (contain["orderID"], contain["wineID"], contain["quantity"])
            )

        
        is_paired = generate_is_paired(wines, num_pairs)
        for pair in is_paired:
            cursor.execute(
                "INSERT INTO IsPaired (wineID1, wineID2) VALUES (%s, %s)",
                (pair["wineID1"], pair["wineID2"])
            )

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
        cursor = conn.cursor(dictionary=True)  
        cursor.execute("""
            SELECT w.wineID, w.name, w.type, w.price, w.country, w.alcoholPercentage,
                   cw.numberInCollection, cw.specialPackaging,
                   CASE WHEN cw.wineID IS NOT NULL THEN TRUE ELSE FALSE END AS isCollectionWine
            FROM Wine w
            LEFT JOIN CollectionWine cw ON w.wineID = cw.wineID
        """)
        wines = cursor.fetchall()
        conn.close()
        return jsonify(wines), 200
    except Exception as e:
        app.logger.error(f"Error fetching wines: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/report/top-spender", methods=["GET"])
def get_top_spender_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to find the customer who spent the most on wines
    cursor.execute("""
        SELECT c.customerID, c.firstname, c.surname, SUM(w.price * co.quantity) as total_spent
        FROM Customer c
        JOIN `Order` o ON c.customerID = o.customerID
        JOIN Contains co ON o.orderID = co.orderID
        JOIN Wine w ON co.wineID = w.wineID
        GROUP BY c.customerID
        ORDER BY total_spent DESC
        LIMIT 1
    """)
    customer = cursor.fetchone()

    if customer:
        customer_id = customer["customerID"]
        customer_name = f"{customer['firstname']} {customer['surname']}"
        total_spent = customer["total_spent"]

        # Query to find the wines purchased by the customer
        cursor.execute("""
            SELECT w.name, w.type, w.price, w.country, w.alcoholPercentage, co.quantity
            FROM Contains co
            JOIN Wine w ON co.wineID = w.wineID
            JOIN `Order` o ON co.orderID = o.orderID
            WHERE o.customerID = %s
        """, (customer_id,))
        wines = cursor.fetchall()

        report = {
            "customerName": customer_name,
            "totalSpent": total_spent,
            "wines": wines
        }
    else:
        report = {
            "customerName": "No customer found",
            "totalSpent": 0,
            "wines": []
        }

    conn.close()
    return jsonify(report)

@app.route("/api/wines/<int:wine_id>/details", methods=["GET"])
def get_wine_details(wine_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT w.wineID, w.name, w.type, w.price, w.country, w.alcoholPercentage
            FROM Wine w
            WHERE w.wineID = %s
        """, (wine_id,))
        wine_row = cursor.fetchone()

        if not wine_row:
            conn.close()
            return jsonify({"error": "Wine not found"}), 404

        cursor.execute("""
            SELECT reviewID, customerID, rating, comment
            FROM Review
            WHERE wineID = %s
        """, (wine_id,))
        reviews = cursor.fetchall()

        if reviews:
            avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        else:
            avg_rating = 0.0  

        conn.close()

        return jsonify({
            "wine": wine_row,
            "reviews": reviews,
            "averageRating": avg_rating
        }), 200

    except Exception as e:
        app.logger.error(f"Error fetching wine details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/wines/<int:wine_id>/reviews", methods=["POST"])
def add_review(wine_id):
    try:
        data = request.get_json()
        customer_id = data.get("customerID")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not customer_id or not rating:
            return jsonify({"error": "Missing required fields"}), 400
        if int(rating) < 1 or int(rating) > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT wineID FROM Wine WHERE wineID = %s", (wine_id,))
        wine_exists = cursor.fetchone()
        if not wine_exists:
            conn.close()
            return jsonify({"error": "Wine does not exist"}), 404

        cursor.execute("SELECT customerID FROM Customer WHERE customerID = %s", (customer_id,))
        customer_exists = cursor.fetchone()
        if not customer_exists:
            conn.close()
            return jsonify({"error": "Customer does not exist"}), 404

        cursor.execute(
            "INSERT INTO Review (customerID, wineID, rating, comment) VALUES (%s, %s, %s, %s)",
            (customer_id, wine_id, rating, comment)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Review added successfully"}), 201

    except Exception as e:
        app.logger.error(f"Error adding review: {e}")
        return jsonify({"error": str(e)}), 500

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
    

@app.route("/api/reports/collection-wine-sales", methods=["GET"])
def collection_wine_sales_report():
    """
    Returns a JSON report for all Collection Wines
    that have completed orders between 2023-01-01 and 2023-12-31,
    including total orders, quantity sold, average rating, and more.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                W.name AS Wine_Name,
                W.type AS Wine_Type,
                CW.numberInCollection AS Number_in_Collection,
                CW.specialPackaging AS Special_Packaging,
                COUNT(DISTINCT O.orderID) AS Total_Orders,
                SUM(C.quantity) AS Total_Quantity_Sold,
                AVG(R.rating) AS Average_Rating,
                COUNT(R.reviewID) AS Total_Reviews
            FROM
                Wine W
                INNER JOIN CollectionWine CW ON W.wineID = CW.wineID
                INNER JOIN Contains C ON W.wineID = C.wineID
                INNER JOIN `Order` O ON C.orderID = O.orderID
                LEFT JOIN Review R ON W.wineID = R.wineID
            WHERE
                O.status = 'Completed'
                AND O.orderDate BETWEEN '2023-01-01' AND '2023-12-31'
            GROUP BY
                W.name, W.type, CW.numberInCollection, CW.specialPackaging
            ORDER BY
                Total_Orders DESC,
                Average_Rating DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return jsonify(results), 200

    except Exception as e:
        app.logger.error(f"Error generating Collection Wine Sales Report: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/report")
def report_page():
  
    return render_template("report.html")


@app.route("/wine/<int:wine_id>")
def wine_detail(wine_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch wine details
        cursor.execute("SELECT * FROM Wine WHERE wineID = %s", (wine_id,))
        wine = cursor.fetchone()
        if not wine:
            conn.close()
            return "Wine not found", 404
        
        # Fetch customers
        cursor.execute("SELECT customerID, firstname, surname FROM Customer")
        customers = cursor.fetchall()
        
        conn.close()
        return render_template("wine_detail.html", wine_id=wine["wineID"], wine=wine, customers=customers)

    except Exception as e:
        app.logger.error(f"Error fetching wine details: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route("/collection-wine-report")
def collection_wine_report_page():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                W.name AS Wine_Name,
                W.type AS Wine_Type,
                CW.numberInCollection AS Number_in_Collection,
                CW.specialPackaging AS Special_Packaging,
                COUNT(DISTINCT O.orderID) AS Total_Orders,
                SUM(C.quantity) AS Total_Quantity_Sold,
                AVG(R.rating) AS Average_Rating,
                COUNT(R.reviewID) AS Total_Reviews
            FROM
                Wine W
                INNER JOIN CollectionWine CW ON W.wineID = CW.wineID
                INNER JOIN Contains C ON W.wineID = C.wineID
                INNER JOIN `Order` O ON C.orderID = O.orderID
                LEFT JOIN Review R ON W.wineID = R.wineID
            WHERE
                O.status = 'Completed'
            GROUP BY
                W.name, W.type, CW.numberInCollection, CW.specialPackaging
            ORDER BY
                Total_Orders DESC, Average_Rating DESC
        """

        cursor.execute(query)
        report_data = cursor.fetchall()
        conn.close()

        return render_template("review_report.html", report=report_data)  # Use the correct filename here

    except Exception as e:
        app.logger.error(f"Error fetching report: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
