import boto3
import json
from botocore.exceptions import ClientError

# Define the required variables
model_id = 'meta.llama3-8b-instruct-v1:0'  # Model ID for Meta Llama 3 8B Instruct

# Create the Boto3 client for Bedrock Runtime
bedrock_runtime_client = boto3.client("bedrock-runtime")

while True:
    # Display menu options to the user
    print("Select an option:")
    print("1) Ask the model a question")
    print("2) Exit")

    # Get user input
    user_choice = input("Enter your choice (1 or 2): ")

    if user_choice == "1":
        # Prompt the user for their question
        user_question = input("Please enter your question: ")

        # Format the question into the model's input format
        formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{user_question}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

        # Prepare the request payload with the required inference configuration
        native_request = {
            "prompt": formatted_prompt,
            "max_gen_len": 50,     # Limits the response to 50 tokens
            "temperature": 0.1,    # Reduces randomness
            "top_p": 0.9           # Restricts token selection to the most probable options
        }

        # Convert the native request to JSON
        request = json.dumps(native_request)

        try:
            # Invoke the model with the request
            response = bedrock_runtime_client.invoke_model(modelId=model_id, body=request)

            # Decode the response body
            model_response = json.loads(response["body"].read())

            # Extract the generated text from the response
            response_text = model_response["generation"]

            print(f"Model Response: {response_text}")

        except (ClientError, Exception) as e:
            print(f"ERROR: Could not invoke '{model_id}'. Reason: {e}")

    elif user_choice == "2":
        # Exit the program
        print("Exiting the program. Goodbye!")
        break

    else:
        # Invalid input, prompt user again
        print("Invalid input. Please enter 1 or 2.")
