from flask import Flask, jsonify, request, render_template
from random_data_generator import generate_customers, generate_wines, populate_database  # Import the generator
import logging

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # Render the GUI

@app.route("/api/customers", methods=["POST"])
def add_customer():
    customer = request.json
    # Here you would add code to insert the customer into your database
    # For example:
    # db.insert_customer(customer)
    return jsonify({"message": "Customer added successfully"}), 201

@app.route("/api/wines", methods=["POST"])
def add_wine():
    wine = request.json
    # Here you would add code to insert the wine into your database
    # For example:
    # db.insert_wine(wine)
    return jsonify({"message": "Wine added successfully"}), 201

@app.route("/populate-database", methods=["POST"])
def populate_database_endpoint():
    try:
        populate_database()  # Run the randomization script
        return jsonify({"message": "Database populated successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error populating database: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
