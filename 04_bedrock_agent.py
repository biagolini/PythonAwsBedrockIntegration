import boto3
import uuid
from botocore.exceptions import ClientError

# Get clients
bedrock_agent_client = boto3.client('bedrock-agent')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

# Function to retrieve the agent ID by its name.
def get_agent_id_by_name(client, agent_name):
    try:
        paginator = client.get_paginator('list_agents')
        for page in paginator.paginate():
            for agent in page.get('agentSummaries', []):
                if agent.get('agentName') == agent_name:
                    return agent.get('agentId')
    except ClientError as e:
        print(f"Error while listing agents: {e}")
        return None
    print(f"Agent with name '{agent_name}' not found.")
    return None

# Function to retrieve the alias ID for a specific agent.
def get_agent_alias_id(client, agent_id, alias_name):
    try:
        paginator = client.get_paginator('list_agent_aliases')
        for page in paginator.paginate(agentId=agent_id):
            for alias in page.get('agentAliasSummaries', []):
                if alias.get('agentAliasName') == alias_name:
                    return alias.get('agentAliasId')
    except ClientError as e:
        print(f"Error while listing agent aliases: {e}")
        return None
    print(f"Alias with name '{alias_name}' not found for agent '{agent_id}'.")
    return None

# Function to invoke an agent with the specified parameters.
def invoke_agent(client, agent_id, alias_id, session_id, query):
    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=session_id,
            inputText=query
        )
        # Process the EventStream to compose the complete response
        completion = response.get('completion')
        if completion is None:
            print("No response received from the agent.")
            return None

        full_response = ""
        for event in completion:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    full_response += chunk['bytes'].decode('utf-8')
            elif 'trace' in event:
                trace = event['trace']
                print("Trace received:", trace)
            else:
                print("Unexpected event received:", event)
        return full_response
    except ClientError as e:
        print(f"Error while invoking agent: {e}")
        return None

# Function to ask a question to a Bedrock agent.
def ask_a_question(agent_name, alias_name, query):

    # Retrieve IDs
    agent_id = get_agent_id_by_name(bedrock_agent_client, agent_name)
    if not agent_id:
        print("Failed to retrieve the agent ID.")
        return None
    
    alias_id = get_agent_alias_id(bedrock_agent_client, agent_id, alias_name)
    if not alias_id:
        print("Failed to retrieve the alias ID.")
        return None

    # Generate session_id and invoke agent
    session_id = str(uuid.uuid4())
    response_text = invoke_agent(bedrock_agent_runtime_client, agent_id, alias_id, session_id, query)
    print("Agent response:", response_text)
    return response_text

# Calls to the function with different queries
# Foundation Model Base Query
ask_a_question(query='Who is Michael Jordan?', agent_name='notable-celebrity-agent', alias_name='develop-v1')

# Knowledge Base Query
ask_a_question(query='Who is Alicia Torrence?', agent_name='notable-celebrity-agent', alias_name='develop-v1')

# Lambda Query
ask_a_question(query='Me entregue o link da página do Wikipedia do Pelé.', agent_name='notable-celebrity-agent', alias_name='develop-v1')
