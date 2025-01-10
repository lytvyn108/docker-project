import random
import requests
from faker import Faker

# Initialize Faker for random data generation
fake = Faker()

# Base URL of your API (change to match your setup)

BASE_URL = "http://web:80/api"


# Generate random data for Customers
def generate_customers(num_customers):
    customers = []
    for _ in range(num_customers):
        customer = {
            "firstname": fake.first_name(),
            "surname": fake.last_name(),
            "email": fake.email(),
        }
        customers.append(customer)
    return customers

# Generate random data for Wines
def generate_wines(num_wines):
    wine_types = ["Red", "White", "Rosé", "Sparkling"]
    countries = ["France", "Italy", "USA", "Spain", "Germany"]
    wines = []
    for _ in range(num_wines):
        wine = {
            "name": fake.word().capitalize() + " Wine",
            "type": random.choice(wine_types),
            "price": round(random.uniform(5, 500), 2),
            "country": random.choice(countries),
            "alcoholPercentage": round(random.uniform(10, 15), 2),
        }
        wines.append(wine)
    return wines

# Generate random data for Orders
def generate_orders(customers, wines, num_orders):
    orders = []
    for _ in range(num_orders):
        customer = random.choice(customers)
        order = {
            "customerID": customer["customerID"],
            "status": random.choice(["Processing", "Shipped", "Delivered"]),
            "deliveryPrice": round(random.uniform(5, 50), 2),
        }
        orders.append(order)
    return orders

# Send POST requests to the API to insert data
def send_data_to_api(endpoint, data_list):
    for data in data_list:
        response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
        if response.status_code == 201:
            print(f"Successfully added {data} to {endpoint}")
        else:
            print(f"Failed to add {data} to {endpoint}: {response.text}")

# Main function to generate and send data
def populate_database():
    num_customers = 10
    num_wines = 10

    customers = generate_customers(num_customers)
    wines = generate_wines(num_wines)

    # Insert customers into the database
    for customer in customers:
        response = requests.post(f"{BASE_URL}/customers", json=customer)
        if response.status_code != 201:
            raise Exception(f"Failed to insert customer: {response.json()}")

    # Insert wines into the database
    for wine in wines:
        response = requests.post(f"{BASE_URL}/wines", json=wine)
        if response.status_code != 201:
            raise Exception(f"Failed to insert wine: {response.json()}")

if __name__ == "__main__":
    populate_database()
