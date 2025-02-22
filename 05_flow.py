import boto3
from botocore.exceptions import ClientError

# Creating a client for AWS Bedrock Agent Runtime
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

# Defines a function that invokes a flow from AWS Bedrock Agent Runtime to process a document with a specific flow identifier.
def invoke_bedrock_flow(document, flow_id, flow_alias_id):
    """
    Invokes a flow from AWS Bedrock Agent Runtime with the provided parameters.

    :param document: The content of the document to be processed.
    :param flow_id: The flow identifier.
    :param flow_alias_id: The alias identifier of the flow.
    :return: The output document if the flow is successful, otherwise returns an error message.
    """
    try:
        # Sending a request to invoke the specified flow
        response = bedrock_agent_runtime_client.invoke_flow(
            flowIdentifier=flow_id,
            flowAliasIdentifier=flow_alias_id,
            inputs=[
                {
                    "content": {
                        "document": document
                    },
                    "nodeName": "FlowInputNode",
                    "nodeOutputName": "document"
                }
            ]
        )

        result = {}

        # Processing the flow response and updating the results dictionary
        for event in response.get("responseStream", []):
            result.update(event)

        # Checking if the flow execution was successful
        if result.get('flowCompletionEvent', {}).get('completionReason') == 'SUCCESS':
            return result.get('flowOutputEvent', {}).get('content', {}).get('document', {})
        else:
            return f"Flow invocation failed: {result.get('flowCompletionEvent', {}).get('completionReason', 'Unknown reason')}"
    
    except ClientError as error:
        return f"{error}"

# Update the following variables with your Flow ID and Flow Alias ID.
# These details are available in the AWS console. Navigate to the Flow Console:
# https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/flows 
# and access your flow.
# 
# Alternatively, you can obtain this information programmatically using the 
# `list_flow_versions` and `list_flow_aliases` methods from the Bedrock Agent SDK:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent.html
flow_id='YOURFLOWID'
flow_alias_id='YOURALIASID'

# Testing order delivery status retrieval
order_status_request = {
  "userInput": "What is the delivery status for my order?",
  "orderId": "9c73e91f-8dbb-4344-95af-e850b91658b7"
}

# Invoking the flow for delivery tracking
response = invoke_bedrock_flow(order_status_request, flow_id=flow_id, flow_alias_id=flow_alias_id)
print("Order Delivery Status Output:\n", response)

# Testing business information retrieval
business_info_request = {
  "userInput": "In which city is the confectionery Nana Sabor Natural located?",
  "orderId": ""
}

# Invoking the flow to obtain business information
response = invoke_bedrock_flow(business_info_request, flow_id=flow_id, flow_alias_id=flow_alias_id)
print("\n\nBusiness Information Output:\n", response)

# Testing general questions to obtain responses from LLM
other_request = {
  "userInput": "Could you list some benefits of adopting a vegan diet?",
  "orderId": ""
}

# Invoking the flow to answer a general question
response = invoke_bedrock_flow(other_request, flow_id=flow_id, flow_alias_id=flow_alias_id)
print("\n\nGeneral Question Output:\n", response)
