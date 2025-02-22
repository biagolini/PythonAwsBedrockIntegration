import boto3
import uuid
from datetime import datetime, timedelta, timezone
import random

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Select the table
table = dynamodb.Table("VeganSweetOrders")

# Sample order statuses
statuses = ["Processing", "Shipped", "Delivered", "Cancelled"]
descriptions = [
    "Vegan chocolate box",
    "Almond caramel bars",
    "Peanut butter cookies",
    "Gluten-free brownies",
    "Organic fruit gummies",
    "Sugar-free dark chocolate",
    "Vegan marshmallow pack",
    "Cashew coconut truffles",
    "Hazelnut nougat bars",
    "Oatmeal raisin cookies"
]

# Generate and insert 25 sample records
for _ in range(25):
    order_data = {
        "order_id": str(uuid.uuid4()),  # Generate a unique ID
        "order_date": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
        "status": random.choice(statuses),
        "description": random.choice(descriptions),
        "customer_id": str(random.randint(1000, 9999)),  # Random customer ID
        "rating": random.randint(1, 5)  # Random rating from 1 to 5
    }

    table.put_item(Item=order_data)

print("Sample data inserted into the table.")
