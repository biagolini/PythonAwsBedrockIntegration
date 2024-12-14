import boto3
from botocore.exceptions import ClientError
# import warnings  # Uncomment if using warnings for the alternative handling method

# Initialize the Bedrock client
bedrock_client = boto3.client('bedrock')
bedrock_runtime_client = boto3.client('bedrock-runtime')

# Function to retrieve the guardrail ID and latest version by name
def get_guardrail_id_by_name(guardrail_name):
    try:
        response = bedrock_client.list_guardrails()
    except ClientError as e:
        # Handle errors while listing guardrails
        print(f"Error while listing guardrails: {e}")
        return None

    for guardrail in response.get('guardrails', []):
        if guardrail.get('name') == guardrail_name:
            return guardrail.get('id')
            
    # Two options for handling when the guardrail is not found:
    
    # Option 1: Terminate execution by raising an error.
    # This stops the program immediately and signals that the issue must be resolved.
    raise ValueError(f"Guardrail with the name '{guardrail_name}' not found.")
    
    # Option 2: Issue a warning and continue execution.
    # Uncomment the following lines to use this option. Requires the 'warnings' import.
    # warnings.warn(f"Guardrail with the name '{guardrail_name}' not found.")  
    # return None

# Function to ask a query using the guardrail and analyze the response
def ask_query(guardrail_name, query, guardrail_id=None, guardrail_version='DRAFT', source='INPUT'):
    block_reasons = []
    # Retrieve the guardrail ID and latest version
    if not guardrail_id:
        guardrail_id = get_guardrail_id_by_name(guardrail_name)
        if not guardrail_id:
            return block_reasons
    try:
        # Apply the guardrail
        response = bedrock_runtime_client.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source=source,
            content=[
                {
                    'text': {
                        'text': query
                    }
                }
            ]
        )
    except ClientError as e:
        # Handle errors while applying the guardrail
        print(f"Error while applying guardrail: {e}")
        return block_reasons

    # Analyze the response
    action = response.get('action', 'NONE')
    if action == 'GUARDRAIL_INTERVENED':
        assessments = response.get('assessments', [])
        for assessment in assessments:
            if 'topicPolicy' in assessment:
                topics = assessment['topicPolicy'].get('topics', [])
                for topic in topics:
                    if topic.get('action') == 'BLOCKED':
                        block_reasons.append(f"Topic '{topic.get('name')}' was blocked.")
            if 'contentPolicy' in assessment:
                filters = assessment['contentPolicy'].get('filters', [])
                for filter in filters:
                    if filter.get('action') == 'BLOCKED':
                        block_reasons.append(f"Content filter '{filter.get('type')}' was blocked with confidence '{filter.get('confidence')}'.")
            if 'wordPolicy' in assessment:
                custom_words = assessment['wordPolicy'].get('customWords', [])
                for word in custom_words:
                    if word.get('action') == 'BLOCKED':
                        block_reasons.append(f"Custom word '{word.get('match')}' was blocked.")
                managed_words = assessment['wordPolicy'].get('managedWordLists', [])
                for word in managed_words:
                    if word.get('action') == 'BLOCKED':
                        block_reasons.append(f"Managed word '{word.get('match')}' of type '{word.get('type')}' was blocked.")
            if 'sensitiveInformationPolicy' in assessment:
                pii_entities = assessment['sensitiveInformationPolicy'].get('piiEntities', [])
                for entity in pii_entities:
                    if entity.get('action') == 'BLOCKED':
                        block_reasons.append(f"PII entity '{entity.get('type')}' was blocked.")
                regexes = assessment['sensitiveInformationPolicy'].get('regexes', [])
                for regex in regexes:
                    if regex.get('action') == 'BLOCKED':
                        block_reasons.append(f"Regex '{regex.get('name')}' matched and was blocked.")
            if 'contextualGroundingPolicy' in assessment:
                filters = assessment['contextualGroundingPolicy'].get('filters', [])
                for filter in filters:
                    if filter.get('action') == 'BLOCKED':
                        block_reasons.append(f"Contextual grounding filter '{filter.get('type')}' was blocked with score '{filter.get('score')}' and threshold '{filter.get('threshold')}'.")
    return block_reasons

# Example usage with two queries
# The first query contains a question that may trigger the guardrail and get blocked.
# The second query contains a neutral question that should pass without intervention.

# Query that is likely to be flagged and blocked by the guardrail
ask_query(guardrail_name='offensive-content-filter', query="Who is Michael Phelps?")

# Query that is unlikely to be flagged and should pass through the guardrail
ask_query(guardrail_name='offensive-content-filter', query="Who is Pelé?")
