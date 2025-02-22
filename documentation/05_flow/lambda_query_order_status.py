import json
import boto3
import datetime

# Initialize AWS Clients
dynamodb_client = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Configuration
TABLE_NAME = "VeganSweetOrders"
ENABLE_LOG_EXPORT = False # Configuration to enable or disable log export
BUCKET_NAME = 'name-of-your-s3-bucket-for-logging'  # Placeholder for the S3 bucket name

# Reference to the DynamoDB table
table = dynamodb_client.Table(TABLE_NAME)

def export_to_s3(content, filename):
    """
    Exports content to an S3 bucket.
    
    :param content: Content to be saved
    :param filename: File name path in the bucket
    """
    if not ENABLE_LOG_EXPORT:
        print("Log export is disabled. Skipping export to S3.")
        return

    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=json.dumps(content))
    except Exception as e:
        print(f"Error exporting to S3: {str(e)}")

def lambda_handler(event, context):
    """
    Lambda function to retrieve an order status from DynamoDB and log the event to S3.

    :param event: Incoming event payload
    :param context: AWS Lambda context
    :return: Order status or "Unknown" if not found
    """
    try:
        # Log the received event
        print("Received event:", json.dumps(event))

        # Extract aliasId for organizing logs in S3
        alias_id = event.get("flow", {}).get("aliasId", "unknown_alias")

        # Extract inputs from event
        inputs = event.get("node", {}).get("inputs", [])

        # Determine which input to use (inspired by the provided logic)
        if len(inputs) == 1:
            order_id = inputs[0].get("value")
        else:
            order_id = next((item["value"] for item in inputs if item["name"] == "codeHookInput"), None)

        # Validate order_id
        if not order_id:
            print("Error: Missing order_id in event payload")
            return "Unknown"
        # Query DynamoDB for the order status
        response = table.get_item(Key={'order_id': order_id})

        # Extract order status or return "Unknown"
        order_status = response.get('Item', {}).get('status', "Unknown")

        # Generate timestamped log file name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        file_path = f"flow/dynamo/{alias_id}/{timestamp}.json"

        # Log the event to S3
        export_to_s3(event, file_path)

        return order_status

    except Exception as e:
        print("Error:", str(e))

        # Log error details to S3
        error_msg = {"error": str(e)}
        error_path = "flow/dynamo/errors/" + datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".json"
        export_to_s3(error_msg, error_path)

        return "Unknown"