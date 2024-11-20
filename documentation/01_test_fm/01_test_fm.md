# AWS Bedrock Model Invocation with Interactive Prompt for User Questions

This project demonstrates how to integrate Python with AWS Bedrock to invoke foundation models, specifically leveraging the Meta Llama 3 8B Instruct model. It includes an interactive menu allowing users to ask questions dynamically, replacing static prompts with user-provided input.

## Overview

The script enables interaction with AWS Bedrock to process user queries and generate responses from the foundation model. It employs the `InvokeModel` API for stateless requests, making it suitable for direct question-response tasks.

## Choosing `InvokeModel` vs. `Converse`

AWS Bedrock provides two main methods for interacting with foundation models: `Converse` and `InvokeModel`.

- **`Converse`** maintains conversational context across multiple interactions, which is ideal for chatbot applications where maintaining context is important.
- **`InvokeModel`**, used in this demo, is intended for single, stateless requests where maintaining conversation context is not required.

In this project, we utilize the `InvokeModel` API as the task is straightforward and doesn’t benefit from context continuity. This choice simplifies integration and avoids unnecessary overhead.

## Prerequisites

To run this project, you’ll need:
- An AWS account with access to Bedrock services.
- AWS credentials configured with access to the Bedrock service.
- Python 3, and the `boto3` and `botocore` libraries installed.

### References

This project was developed based on the following resources:
- [AWS Bedrock Documentation for Amazon Bedrock Runtime](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_Operations_Amazon_Bedrock_Runtime.html)
- [AWS Boto3 Documentation for Bedrock Invoke Model API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/invoke_model.html)
- [AWS Code Library Bedrock Runtime Python Examples](https://docs.aws.amazon.com/code-library/latest/ug/python_3_bedrock-runtime_code_examples.html)
