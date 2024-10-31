import boto3
import json
from botocore.exceptions import ClientError

# Define the required variables
region_name = 'us-east-1'  # AWS Region where Bedrock is accessible
model_id = 'meta.llama3-8b-instruct-v1:0'  # Model ID for Meta Llama 3 8B Instruct
transcription = "Olá, tudo bem? Fico feliz que você consiga entender o que eu falo. Você pode me chamar de Senhor Carlos Biagolini, é assim que eu gosto de ser chamado."  # Text to be processed by the model

# Load the content of the prompt template from the file and replace {TRANSCRIPTION} with the actual text
with open("prompt.txt", "r", encoding="utf-8") as file:
    prompt_template = file.read()
prompt_text = prompt_template.format(TRANSCRIPTION=transcription)

# Embed the prompt in Llama 3's instruction format
formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{prompt_text}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

# Prepare the request payload with the required inference configuration
native_request = {
    "prompt": formatted_prompt,
    "max_gen_len": 50,     # Limits the response to 50 tokens, as only the name is needed.
    "temperature": 0.1,    # Reduces randomness, encouraging a more predictable and direct response.
    "top_p": 0.9           # Restricts token selection to the most probable options, which can help correct minor transcription errors.
}

# Convert the native request to JSON
request = json.dumps(native_request)

# Create the Boto3 client for Bedrock Runtime
client = boto3.client("bedrock-runtime", region_name=region_name)

try:
    # Invoke the model with the request
    response = client.invoke_model(modelId=model_id, body=request)

    # Decode the response body
    model_response = json.loads(response["body"].read())

    # Extract the generated text from the response
    response_text = model_response["generation"]

    # Parse the response text as JSON
    response_json = json.loads(response_text)

    # Access the preferred user alias
    preferred_user_alias = response_json.get("PREFERRED_USER_ALIAS", "No alias found")
    print(f"Preferred User Alias: {preferred_user_alias}")

except (ClientError, Exception) as e:
    print(f"ERROR: Could not invoke '{model_id}'. Reason: {e}")
    exit(1)
