# Amazon Bedrock Testing Project

Welcome to the **Amazon Bedrock Testing Project**! This repository is a collection of Python scripts and supporting materials to explore and test various methods provided by the Amazon Bedrock service. The repository is organized for clarity and ease of use, especially for those studying or experimenting with Amazon Bedrock's capabilities.

## Repository Structure

```
repository/
├── documentation/          # Contains documentation and step-by-step tutorials
├── XX_file_name.py         # Python scripts to test methods of Amazon Bedrock
├── README.md               # This README file
└── requirements.txt        # Specifies boto3 version (boto3==1.35.61)
```

### Python Scripts

The scripts in this repository are organized with numerical prefixes (e.g., `01_example.py`, `02_example.py`). These numbers are simply for the order of creation and do not reflect the complexity or purpose of the code. Each script demonstrates different methods or features of the Bedrock API.

### Amazon Bedrock Clients

Amazon Bedrock provides four distinct clients, each targeting specific functionalities. Examples of their initialization are as follows:

- **Bedrock Client**:  
  ```python
  bedrock_client = boto3.client('bedrock')
  ```
  Used for managing, training, and deploying models.

- **Bedrock Runtime Client**:  
  ```python
  bedrock_runtime_client = boto3.client('bedrock-runtime')
  ```
  Used for real-time inference with deployed models.

- **Bedrock Agent Client**:  
  ```python
  bedrock_agent_client = boto3.client('bedrock-agent')
  ```
  Used for managing, training, and deploying agents and knowledge bases.

- **Bedrock Agent Runtime Client**:  
  ```python
  bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
  ```
  Used for real-time inference with agents or Retrieval-Augmented Generation (RAG) systems.

### Documentation

The `documentation/` folder contains resources, including tutorials and step-by-step guides, to help you create and interact with necessary AWS resources like Knowledge Bases, Guardrails, and Agents. These materials are meant to complement the code examples and provide context when additional AWS setup is required.

## Purpose

This repository is designed as a learning resource for Amazon Bedrock. The code examples are purely for educational purposes and are intended to help users understand and experiment with the service's features.

Before running any scripts, ensure that your AWS credentials are properly configured, and any required resources in the code are pre-created or accessible.



## Contributing

Feel free to submit issues, create pull requests, or fork the repository to help improve the project.

## License and Disclaimer

This project is open-source and available under the MIT License. You are free to copy, modify, and use the project as you wish. However, any responsibility for the use of the code is solely yours. Please use it at your own risk and discretion.