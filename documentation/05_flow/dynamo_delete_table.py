import boto3

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Table name to be deleted
table_name = "VeganSweetOrders"

# Delete the table
response = dynamodb.delete_table(TableName=table_name)

print(f"Table {table_name} is being deleted. Check AWS Console for status.")
