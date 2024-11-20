import boto3
from botocore.exceptions import ClientError

# Initialize the Boto3 clients
bedrock_agent_client = boto3.client('bedrock-agent')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

def test_knowledge_base(knowledge_base_name, query):
    """
    Queries a specific knowledge base in Amazon Bedrock and retrieves relevant content.
    
    :param knowledge_base_name: Name of the knowledge base to query
    :param query: The query to send to the knowledge base
    :return: The retrieved content or an appropriate message
    """
    try:
        # Retrieve the list of knowledge bases
        knowledge_bases_list = bedrock_agent_client.list_knowledge_bases()
        knowledge_bases = knowledge_bases_list.get('knowledgeBaseSummaries', [])

        # Search for the knowledge base ID by name
        knowledge_base_id = None
        for kb in knowledge_bases:
            if kb.get('name') == knowledge_base_name:
                knowledge_base_id = kb.get('knowledgeBaseId')
                break

        if not knowledge_base_id:
            return f"Knowledge Base '{knowledge_base_name}' not found."

        # Call the retrieve function
        response = bedrock_agent_runtime_client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 1  # Return only the most relevant result
                }
            }
        )

        # Process and evaluate the results
        retrieval_results = response.get('retrievalResults', [])
        if retrieval_results:
            result = retrieval_results[0]
            score = result.get('score', 0)
            relevance_threshold = 0.5  # Define an appropriate relevance threshold

            if score >= relevance_threshold:
                content = result.get('content', {}).get('text', 'No content.')
                return content
            else:
                return "No relevant information found for the query."
        else:
            return "No results found for the query."

    except ClientError as error:
        return f"An error occurred: {error}"

# Test 1: Querying a name that exists in the 'athletes-knowledge-bases'.
# Expected result: The correct embedding/document is returned.
result= test_knowledge_base(knowledge_base_name='athletes-knowledge-bases', query="Who is Alicia Torrence?")
print(f"Test 1 Result:\n{result}\n")

# Test 2: Querying the same name in the 'musicians-knowledge-bases'.
# Expected result: No document found, as the person does not exist in this knowledge base.
result= test_knowledge_base(knowledge_base_name='musicians-knowledge-bases', query="Who is Alicia Torrence?")
print(f"Test 2 Result:\n{result}\n")

# Test 3: Querying a name that does not exist in the 'athletes-knowledge-bases'.
# Expected result: No document found, as the name is not in this knowledge base.
result= test_knowledge_base(knowledge_base_name='athletes-knowledge-bases', query="Who is Elena Rivera?")
print(f"Test 3 Result:\n{result}\n")
