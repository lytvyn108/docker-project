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

# Generate random data for CollectionWines
def generate_collection_wines(wines, num_collection_wines):
    collection_wines = []
    used_wine_ids = set()
    for _ in range(num_collection_wines):
        wine = random.choice(wines)
        while wine["wineID"] in used_wine_ids:
            wine = random.choice(wines)
        used_wine_ids.add(wine["wineID"])
        collection_wine = {
            "wineID": wine["wineID"],  # Ensure this matches the key in the Wine table
            "numberInCollection": random.randint(1, 100),
            "specialPackaging": fake.word().capitalize() + " Packaging",
        }
        collection_wines.append(collection_wine)
    return collection_wines

# Generate random data for Orders
def generate_orders(customers, num_orders):
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

def generate_contains(orders, wines, num_contains):
    contains = []
    used_combinations = set()
    for _ in range(num_contains):
        order = random.choice(orders)
        wine = random.choice(wines)
        combination = (order["orderID"], wine["wineID"])
        while combination in used_combinations:
            order = random.choice(orders)
            wine = random.choice(wines)
            combination = (order["orderID"], wine["wineID"])
        used_combinations.add(combination)
        contain = {
            "orderID": order["orderID"],
            "wineID": wine["wineID"],
            "quantity": random.randint(1, 10)
        }
        contains.append(contain)
    return contains

def generate_is_paired(wines, num_pairs):
    is_paired = []
    used_combinations = set()
    for _ in range(num_pairs):
        wine1, wine2 = random.sample(wines, 2)
        combination = (wine1["wineID"], wine2["wineID"])
        while combination in used_combinations or (wine2["wineID"], wine1["wineID"]) in used_combinations:
            wine1, wine2 = random.sample(wines, 2)
            combination = (wine1["wineID"], wine2["wineID"])
        used_combinations.add(combination)
        pair = {
            "wineID1": wine1["wineID"],
            "wineID2": wine2["wineID"]
        }
        is_paired.append(pair)
    return is_paired

def generate_reviews(customers, wines, num_reviews):
    reviews = []
    for _ in range(num_reviews):
        customer = random.choice(customers)
        wine = random.choice(wines)
        review = {
            "customerID": customer["customerID"],
            "wineID": wine["wineID"],
            "rating": random.randint(1, 5),
            "comment": fake.text()
        }
        reviews.append(review)
    return reviews

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
