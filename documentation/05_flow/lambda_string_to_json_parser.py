import json
import boto3
import datetime

# Initialize AWS Clients
s3_client = boto3.client('s3')

# Configuration for log export
ENABLE_LOG_EXPORT = False # Configuration to enable or disable log export
BUCKET_NAME = 'name-of-your-s3-bucket-for-logging'  # Placeholder for the S3 bucket name

def export_to_s3(content, filename):
    """
    Exports content to a JSON file in S3.
    
    :param content: Content to be exported
    :param filename: File name in the bucket
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
    Lambda function to process the event and save the JSON to S3.
    
    :param event: Event received
    :param context: Lambda execution context
    :return: Extracted and converted JSON or an error JSON object in case of failure
    """
    try:
        # Extracting aliasId for folder name in S3
        alias_id = event.get("flow", {}).get("aliasId", "unknown_alias")
        
        # Extracting and converting the JSON from "value"
        inputs = event.get("node", {}).get("inputs", [])
        
        # Determine which input to use
        if len(inputs) == 1:
            # If there is only one input, use its value directly
            value_str = inputs[0].get("value")
        else:
            # If multiple inputs exist, look for 'codeHookInput'
            # This value is set by the user in AWS Bedrock Flow configuration
            # If the user customizes this parameter, they should update this logic accordingly
            value_str = next((item["value"] for item in inputs if item["name"] == "codeHookInput"), None)
        
        if not value_str:
            raise ValueError("Field 'value' not found within 'inputs'")
        
        # Decoding the JSON string inside the value
        parsed_json = json.loads(value_str)
        
        # Generating timestamp for file name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        file_path = f"flow/parser/{alias_id}/{timestamp}.json"
        
        # Exporting to S3
        export_to_s3(event, file_path)
        
        return parsed_json
    except Exception as e:
        error_msg = {"error": str(e)}
        print(f"Error processing Lambda: {str(e)}")
        
        # Ensure error is also logged in S3 for debugging
        error_path = "flow/parser/errors/" + datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".json"
        export_to_s3(error_msg, error_path)
        
        return error_msg
