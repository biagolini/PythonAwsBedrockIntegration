import boto3

# Initialize the Bedrock client
bedrock_client = boto3.client('bedrock')
# Initialize the Bedrock Runtime client
bedrock_runtime_client = boto3.client('bedrock-runtime')

# Function to retrieve the guardrail ID and latest version by name
def get_guardrail_details_by_name(guardrail_name):
    response = bedrock_client.list_guardrails()
    for guardrail in response.get('guardrails', []):
        if guardrail.get('name') == guardrail_name:
            return guardrail.get('id'), guardrail.get('version')
    return None, None

# Function to ask a question using the guardrail and analyze the response
def ask_question(guardrail_name, question):
    # Retrieve the guardrail ID and latest version
    guardrail_id, guardrail_version = get_guardrail_details_by_name(guardrail_name)

    if guardrail_id and guardrail_version:        
        # Apply the guardrail
        response = bedrock_runtime_client.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source='INPUT',  # or 'OUTPUT' depending on the context
            content=[
                {
                    'text': {
                        'text': question
                    }
                }
            ]
        )

        # Analyze the response
        action = response.get('action', 'NONE')
        if action == 'GUARDRAIL_INTERVENED':
            assessments = response.get('assessments', [])
            reasons = []
            for assessment in assessments:
                if 'topicPolicy' in assessment:
                    topics = assessment['topicPolicy'].get('topics', [])
                    for topic in topics:
                        if topic.get('action') == 'BLOCKED':
                            reasons.append(f"Topic '{topic.get('name')}' was blocked.")
                if 'contentPolicy' in assessment:
                    filters = assessment['contentPolicy'].get('filters', [])
                    for filter in filters:
                        if filter.get('action') == 'BLOCKED':
                            reasons.append(f"Content filter '{filter.get('type')}' was blocked with confidence '{filter.get('confidence')}'.")
                if 'wordPolicy' in assessment:
                    custom_words = assessment['wordPolicy'].get('customWords', [])
                    for word in custom_words:
                        if word.get('action') == 'BLOCKED':
                            reasons.append(f"Custom word '{word.get('match')}' was blocked.")
                    managed_words = assessment['wordPolicy'].get('managedWordLists', [])
                    for word in managed_words:
                        if word.get('action') == 'BLOCKED':
                            reasons.append(f"Managed word '{word.get('match')}' of type '{word.get('type')}' was blocked.")
                if 'sensitiveInformationPolicy' in assessment:
                    pii_entities = assessment['sensitiveInformationPolicy'].get('piiEntities', [])
                    for entity in pii_entities:
                        if entity.get('action') == 'BLOCKED':
                            reasons.append(f"PII entity '{entity.get('type')}' was blocked.")
                    regexes = assessment['sensitiveInformationPolicy'].get('regexes', [])
                    for regex in regexes:
                        if regex.get('action') == 'BLOCKED':
                            reasons.append(f"Regex '{regex.get('name')}' matched and was blocked.")
                if 'contextualGroundingPolicy' in assessment:
                    filters = assessment['contextualGroundingPolicy'].get('filters', [])
                    for filter in filters:
                        if filter.get('action') == 'BLOCKED':
                            reasons.append(f"Contextual grounding filter '{filter.get('type')}' was blocked with score '{filter.get('score')}' and threshold '{filter.get('threshold')}'.")

            if reasons:
                print(f"Question: '{question}' was filtered for the following reasons:")
                for reason in reasons:
                    print(f"  - {reason}")
            else:
                print(f"Question: '{question}' was filtered, but no specific reasons were provided.")
        else:
            print(f"Question: '{question}' was not filtered.")
    else:
        print(f"Guardrail with the name '{guardrail_name}' not found.")

# Define the name of the guardrail
guardrail_name = 'offensive-content-filter'

# Ask two independent questions
ask_question(guardrail_name, "Who is Michael Phelps?")
ask_question(guardrail_name, "Who is Pelé?")
