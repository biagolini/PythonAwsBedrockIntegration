import boto3

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the table name
table_name = "VeganSweetOrders"

# Create the table
response = dynamodb.create_table(
    TableName=table_name,
    AttributeDefinitions=[
        {'AttributeName': 'order_id', 'AttributeType': 'S'}
    ],
    KeySchema=[
        {'AttributeName': 'order_id', 'KeyType': 'HASH'}
    ],
    BillingMode='PAY_PER_REQUEST',  # Serverless and cost-efficient
)

print(f"Table {table_name} is being created. Check AWS Console for status.")
