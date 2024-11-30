import boto3
import json
from botocore.exceptions import ClientError

# Define constants for model configuration
MODEL_ID = 'meta.llama3-8b-instruct-v1:0'  # Model ID for Meta Llama 3 8B Instruct
REGION = 'us-east-1'

# Create the Boto3 client for Bedrock Runtime
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)

# Inference configuration settings
DEFAULT_INFERENCE_CONFIG = {
    "maxTokens": 100,
    "temperature": 0.1,
    "topP": 0.75
}

print("Welcome to the AWS Bedrock Interactive Program!")
print("Choose one of the following modes to interact with the model:")

while True:
    print("\nMain Menu:")
    print("1) Interactive Conversation Mode (with context)")
    print("2) Single-Turn Message Mode (no context)")
    print("3) Exit")
    main_choice = input("Enter your choice (1, 2, or 3): ")

    if main_choice == "1":
        print("\n--- Interactive Conversation Mode ---")
        conversation_history = []

        while True:
            print("\nMenu:")
            print("1) Ask a question")
            print("2) Exit")
            user_choice = input("Enter your choice (1 or 2): ")

            if user_choice == "1":
                user_question = input("Enter your question: ")
                try:
                    conversation_history.append({"role": "user", "content": [{"text": user_question}]})

                    response = bedrock_client.converse(
                        modelId=MODEL_ID,
                        messages=conversation_history,
                        inferenceConfig=DEFAULT_INFERENCE_CONFIG
                    )

                    assistant_response = response['output']['message']['content'][0]['text']
                    print(f"Assistant: {assistant_response}")

                    conversation_history.append({"role": "assistant", "content": [{"text": assistant_response}]})

                except (ClientError, Exception) as error:
                    print(f"ERROR: Failed to interact with the model. Details: {error}")
            elif user_choice == "2":
                print("Exiting conversation mode. Returning to main menu.")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")

    elif main_choice == "2":
        print("\n--- Single-Turn Message Mode ---")

        while True:
            print("\nMenu:")
            print("1) Ask a question")
            print("2) Exit")
            user_choice = input("Enter your choice (1 or 2): ")

            if user_choice == "1":
                user_question = input("Enter your question: ")

                formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{user_question}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
                native_request = {
                    "prompt": formatted_prompt,
                    "max_gen_len": 50,
                    "temperature": 0.1,
                    "top_p": 0.9
                }

                try:
                    response = bedrock_client.invoke_model(
                        modelId=MODEL_ID,
                        body=json.dumps(native_request)
                    )

                    model_response = json.loads(response["body"].read())
                    generated_text = model_response["generation"]
                    print(f"Assistant: {generated_text}")

                except (ClientError, Exception) as error:
                    print(f"ERROR: Failed to invoke the model. Details: {error}")
            elif user_choice == "2":
                print("Exiting single-turn message mode. Returning to main menu.")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")

    elif main_choice == "3":
        print("Exiting the program. Goodbye!")
        break

    else:
        print("Invalid input. Please enter 1, 2, or 3.")
