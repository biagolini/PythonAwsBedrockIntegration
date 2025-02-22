# Building a Chatbot with AWS Bedrock Flows

## Overview

Amazon Bedrock Flows is an advanced workflow automation tool designed for developers, DevOps, data scientists, and business users. It enables the creation and management of AI-driven workflows through a no-code/low-code visual interface, simplifying AI-powered automation and orchestration.

This tutorial will guide you through building an AI-powered chatbot using **AWS Bedrock Flows**, designed to handle **order tracking and general inquiries** for a vegan bakery. By leveraging **foundation models (FMs), prompts, AWS Lambda, and Amazon DynamoDB**, we will construct a seamless workflow that allows users to check order statuses and ask business-related questions effortlessly.

With Bedrock Flows, complex AI workflows become more accessible through its visual designer, facilitating integration with various AWS services and ensuring smooth data exchange between components. Furthermore, Bedrock Flows enables the deployment of **immutable workflows**, making it easier to transition from testing to production while maintaining workflow integrity.

For example, a chatbot workflow can incorporate:
- A **Prompt Node** to interpret user queries.
- A **Knowledge Base Node** to retrieve relevant business information.
- An **AWS Lambda Function** to fetch order details from a DynamoDB table.

## Test Environment Setup

To put AWS Bedrock Flows into action, we will create a **workflow for a vegan bakery chatbot**. This chatbot will serve two primary functions:
- **Order Tracking** – Allowing users to check the status of their bakery orders.
- **Business Inquiry Handling** – Answering common questions about the bakery, such as its history, products, and policies.

For demonstration purposes, we will use **randomly generated order data** stored in **Amazon DynamoDB**. To keep the tutorial focused on Bedrock Flows, we will minimize the complexity of external components. However, when implementing this solution in a production environment, it is crucial to follow best security practices, such as **applying the principle of least privilege when configuring AWS Lambda roles**.

By the end of this tutorial, you will have a working chatbot powered by **AWS Bedrock Flows**, capable of efficiently handling user queries while maintaining structured AI-driven automation. Let’s dive in!


## Step-by-Step Implementation

### Step 1: Create a DynamoDB Table

A DynamoDB table will store **dummy order data** for this project.

To create the table:

1.1. Open the **AWS DynamoDB Console**.

1.2. Create a new table with the following attributes:
   - **Primary Key:** `orderId` (String)
   - **Additional Attributes:** `status` (String) representing order status (Processing, Shipped, Delivered, etc.).

1.3. Save and create the table.

For automating table creation with Python scripts, you can automate this process using the provided Python scripts available in the reference GitHub repository: [GitHub Repository](https://github.com/biagolini/PythonAwsBedrockIntegration/tree/main/documentation/05_flow).

```bash
python3 dynamo_create_table.py
python3 dynamo_insert_data.py
python3 dynamo_delete_table.py
```

Proceed to the next steps to integrate this table with AWS Bedrock Flows and build the chatbot.

---

### Step 2: Create AWS Lambda Functions

In this step, we will create AWS Lambda functions to support order tracking and inquiry. Each function has a specific role in the workflow, ensuring smooth data retrieval and processing.

#### Step 2.1: Create IAM Roles

Before creating the Lambda functions, we need to set up two separate **IAM Roles** to grant the necessary permissions.

2.1.1. Open the **AWS IAM Console**.

2.1.2. Create the first IAM Role (**OrderQueryLambdaRole**) with the following permissions:
- **AmazonDynamoDBReadOnlyAccess** (or a custom policy granting read access to the specific table).
- **AWSLambdaBasicExecutionRole** (for logging permissions in CloudWatch).
- (Optional) S3 write access if the user wants to store event logs in S3.

2.1.3. Create the second IAM Role (**JsonFormatLambdaRole**) with the following permissions:
- **AWSLambdaBasicExecutionRole** (for logging permissions in CloudWatch).
- (Optional) S3 write access if the user wants to store event logs in S3.

2.1.4. Attach these roles to their respective Lambda functions as described below.

#### Step 2.2: Create AWS Lambda Function for String-to-JSON Conversion

Since Bedrock Flow does not natively format model outputs as structured JSON, we use a Lambda function to convert the text-based response into a valid JSON object.

2.2.1. Open the **AWS Lambda Console**.

2.2.2. Create a new Lambda function and provide a meaningful name that reflects its purpose. For example: `bedrock-flow-string-to-json-parser`.

2.2.3. Use the **Python 3.x runtime**.

2.2.4. Assign the **JsonFormatLambdaRole** created earlier.

2.2.5. Upload the provided `lambda_string_to_json_parser.py` script from this repository: [GitHub Repository](https://github.com/biagolini/PythonAwsBedrockIntegration/tree/main/documentation/05_flow).

2.2.6. Deploy the function.

2.2.7. Use the `lambda_test_string_to_json_parser.json` file as a test event.

2.2.8. The function includes a section to log received events into an **S3 bucket**. This is purely for educational purposes. If the user intends to store these logs, ensure the IAM Role has S3 write permissions.


#### Step 2.3: Create AWS Lambda Function for Order Query

This Lambda function retrieves order status information from the DynamoDB table. It will be called by the Bedrock Flow to fetch order details.

2.3.1. Open the **AWS Lambda Console**.

2.3.2. Create a new Lambda function and provide a meaningful name that reflects its purpose. For example: `bedrock-flow-dynamo-query-order-status`.

2.3.3. Use the **Python 3.x runtime**.

2.3.4. Assign the **OrderQueryLambdaRole** created earlier.

2.3.5. Upload the provided `lambda_query_order_status.py` script from this repository: [GitHub Repository](https://github.com/biagolini/PythonAwsBedrockIntegration/tree/main/documentation/05_flow).

2.3.6. Deploy the function.

2.3.7. Use the `lambda_test_query_order_status.json` file as a test event, replacing the sample order ID with an actual ID from your DynamoDB table.

2.3.8. The function includes a section to log received events into an **S3 bucket**. This is purely for educational purposes. If the user intends to store these logs, ensure the IAM Role has S3 write permissions.

---

### Step 3: Create a Knowledge Base for Company Information

At this stage, we will set up a **Knowledge Base** that stores documents related to the company. This repository will serve as a data source for answering customer inquiries about the business.

Since the primary focus of this tutorial is **AWS Bedrock Flow**, we will leverage an existing guide on setting up knowledge bases. Follow this tutorial: [Setting up Knowledge Bases on AWS Bedrock](https://medium.com/devops-dev/setting-up-knowledge-bases-on-aws-bedrock-with-amazon-s3-and-mongodb-atlas-20d300bd0e38), adapting it to match your company's requirements. Ensure that:

- The knowledge base name reflects the company in this tutorial.
- The stored documents contain relevant business information. See sample document at this repository: [GitHub Repository](https://github.com/biagolini/PythonAwsBedrockIntegration/tree/main/documentation/05_flow/sample-s3-bedrock-knowledge-bases).

A sample document to be used in the knowledge base is included in the repository of this tutorial. You can upload this file to the knowledge base to simulate real-world use cases.

This knowledge base will later be queried by the Bedrock Flow workflow to provide accurate company-related answers to users.

---

### Step 4: Creating and Configuring Prompts in AWS Bedrock Flows

To ensure the chatbot can correctly interpret and categorize user queries, we will create a structured prompt in AWS Bedrock’s **Prompt Management** tool.  This prompt will receive two input variables and generate a JSON like object as output.

#### Step 4.1: Access Prompt Management

4.1.1. Log into the **AWS Console**.
4.1.2. Navigate to: **Left Menu** → **Build Tools** → **Prompt Management** → **Create Prompt**. Link to Prompt Management: [here](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/prompt-management)

#### Step 4.2: Define the Prompt

Create a new prompt with the following details:

- **Name:** `OrderInquiryPrompt`
- **Description:** `Classifies user queries related to order status and bakery information.`

#### Step 4.3: Define the User Message Format

At `System instructions` use:

```
Rules:
- Do not provide explanations, clarifications, or additional text. Respond only with a structured JSON format.
- If the user input is ambiguous, choose the most appropriate category based on the available information.
- Maintain consistency and avoid variations in formatting or wording.
- Treat any inquiry related to the bakery’s history, founder(s), products, or operations as "businessInfo".
- Questions explicitly mentioning an order ID should be classified as "orderStatus" unless they are unrelated to orders.
- If the user asks about Nana Bakery, even indirectly (e.g., "Who started Nana Bakery?", "Where is Nana Bakery located?"), classify it as "businessInfo".
- Ensure the response is formatted as a JSON object containing the following fields:
  - `intent`: Classification label ("orderStatus", "businessInfo", or "other").
  - `language`: The detected language in English (e.g., "Portuguese", "English").
  - `orderId`: If provided, include the value; otherwise, omit the field.
```

At `User message` request AI to categorize user inputs and format the response in JSON:

```
Determine the intent of the user input:
- "orderStatus" - for queries related to checking order status.
- "businessInfo" - for questions about Nana Vegan Bakery, including its history, founders, operations, and offerings.
- "other" - for any unrelated queries.
Examples:
- "What is the status of my order?" → orderStatus
- "What year was Nana founded?" → businessInfo
- "Who started Nana Bakery?" → businessInfo
- "Where is Nana Bakery located?" → businessInfo
- "Is eating soy dangerous?" → other
User Input: {{userInput}}
Order ID: {{orderId}}
```

#### Step 4.4: Configure Model Execution Parameters

To optimize the performance of the prompt, configure the following parameters:

- **Model Selection:** Choose an appropriate **Foundation Model** (e.g., **Anthropic Claude, Llama 3, Amazon Titan**).
- **Temperature:** Adjust this value to balance response variability, considering the need for determinism versus randomness.
- **Top-P:** Modify this parameter to control response diversity while maintaining coherence.
- **Response Length:** Set an appropriate limit to ensure responses remain concise and relevant.

#### Step 4.5: Test the Prompt

Before deploying the workflow, test the prompt with different sample inputs:

**Sample Input 1 (English):**  

```
userInput: What is the status of my order?
orderId: 1099258a-9ae4-4da1-ac1a-0ea516c10210
```

**Expected Output:**  

```
{
  "intent": "orderStatus",
  "language": "English",
  "orderId": "1099258a-9ae4-4da1-ac1a-0ea516c10210"
}
```

**Sample Input 2 (Portuguese):**  

```
userInput: Comer soja é perigoso?
orderId: 
```

**Expected Output:**  

```
{
  "intent": "other",
  "language": "Portuguese",
  "orderId": null
}
```

#### Step 4.6: Handling the JSON Response in AWS Flow

AWS Bedrock Flows treats AI-generated responses as strings. Therefore, accessing individual elements within the response requires conversion for structured data processing. To achieve this, we use an AWS Lambda function in the next steps to parse the JSON string into an object.

---

### Step 5: Create a Bedrock Flow

5.1. Open the **AWS Bedrock Console**.

5.2. Navigate to **Flows** and click **Create Flow**.

5.3. Enter flow details:
   - **Name:** `VeganBakery`
   - **Description:** `A workflow for a vegan bakery chatbot.`
   - **Service Role:** Create and assign a new service role with necessary permissions.

---

### Step 6: Configure the Flow Input in AWS Bedrock Flows

6.1. When AWS initializes the flow, it includes **Flow Input** and **Flow Output** nodes by default.

6.2. To prevent misconfigurations and ensure clarity in the workflow, **remove the direct connection** between the Flow Input and Flow Output nodes.

6.3. Modify the **Flow Input** node settings. Set the **Output Type** to `Object`. Ensure that the expected input structure includes two variables required for further processing.

6.4. This step is crucial to properly handle multiple input variables before passing them through subsequent workflow components. Proper structuring of the flow input ensures seamless integration with downstream processing nodes.

---

### Step 7: Configure the First Node in AWS Bedrock Flows

7.1. In the **Nodes** panel, under **Code**, select **Lambda** and drag it onto the workflow canvas.

7.2. Click on the **Lambda Node** and assign the Lambda function created in **Step 2.2**.

7.3. Rename the node to `QueryInterpreter` for clarity.

7.4. Select the previously created prompt from **Prompt Management**, named `OrderInquiryPrompt`.

7.5. Choose a prompt version. For development, select **Draft** to use the latest version, while for production, select a specific version to maintain stability.

7.6. Connect the **Flow Input** node to the **Prompt Node** to ensure data flows correctly between components.

7.7. Ensure both required input variables are properly mapped to the node.

7.8. Set the first input expression to `$.data.userInput`.

7.9. Set the second input expression to `$.data.orderId` and verify all settings before finalizing the configuration.

**Note:** For more details on accessing data within objects in AWS Bedrock Flow, refer to the official documentation: [AWS Bedrock Flow Expressions](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-expressions.html?icmpid=docs_bedrock_help_panel_condition_node).

---

## Step 8: Configure the Lambda Node in AWS Bedrock Flows

Due to the limitations at the time of writing this tutorial, there was no native way to make the Node Prompt from the previous step return a JSON object that could be directly processed in the next step. To work around this, we need to use a Lambda function to convert the text output into a structured JSON object that can be used for decision-making.

8.1. In the **Nodes** panel, under **Code**, select **Lambda**.

8.2. Drag the **Lambda Node** onto the workflow canvas.

8.3. Rename the node to **JSONParser** for clarity.

8.4. Click on the **Lambda Node**, then select the Lambda function created in **Step 2.2**.

8.5. Pay special attention to the input name for the Lambda function. The object sent to your Lambda function is structured as a list, so handling the correct object reference is crucial. 

8.6. Modify the output type of the Lambda function node from **String** to **Object** to ensure that subsequent nodes can correctly process the structured JSON output.

**Notes:**
- In the code provided in **Step 2.2**, we used the default `codeHookInput` along with logic to extract content when there is only a single element in the input list. If your Lambda function is expected to handle multiple inputs, additional logic should be implemented to correctly process each element in the list.
- Below is an example of the payload sent by AWS Bedrock Flow to the Lambda function during execution in this tutorial:

```json
{
  "node": {
    "name": "JSONParser",
    "inputs": [
      {
        "name": "codeHookInput",
        "expression": "$.data",
        "value": "{\n  \"intent\": \"orderStatus\",\n  \"language\": \"Portuguese\",\n  \"orderId\": \"1099258a-9ae4-4da1-ac1a-0ea516c10210\"\n}",
        "type": "STRING"
      }
    ]
  },
  "flow": {
    "aliasId": "TSTALIASID",
    "arn": "arn:aws:bedrock:us-east-1:471112955224:flow/V1VO2VSPMT"
  },
  "messageVersion": "1.0"
}
```

By properly configuring this node, we ensure that the workflow can correctly parse and utilize the structured JSON data for subsequent decision-making.

---

### Step 9: Partial Test

To verify that the environment is functioning correctly up to this stage, we will conduct a partial test by connecting the Lambda function to the **Flow Output** node and confirming that data is being processed correctly.

9.1. Connect the **JSONParser Lambda Node** to the **Flow Output** node.

9.2. Save your configurations.

9.3. Send a test input as shown below and check if any errors occur.

If all previous steps have been executed correctly, you should receive a JSON output containing the interpretation implemented in **Prompt Management (Step 4)**.

#### Example Input:

```text
{ 
 "userInput":  "Qual é o status do meu pedido?",
 "orderId": "1099258a-9ae4-4da1-ac1a-0ea516c10210"
}
```

#### Expected Output:

```json
{
  "intent": "orderStatus",
  "orderId": "1099258a-9ae4-4da1-ac1a-0ea516c10210",
  "language": "Portuguese"
}
```

If the expected output is returned, it confirms that the data structure is correctly passing through the flow, from input to processing in the Lambda function, and reaching the output node successfully. The next step will involve configuring the conditional node for decision-making.

---

### Step 10: Configure a Conditional Node in AWS Bedrock Flows

To enable decision-making within AWS Bedrock Flows, we will configure a **Conditional Node**. This node will process the intent extracted from user input and direct the workflow accordingly. 

10.1. In the **Nodes** panel, under **Logic**, select **Condition** and add it to the workflow.

10.2. Assign a meaningful name to the conditional node, such as `ServiceSelector`.

10.3. Rename the input variable to `intent` to enhance clarity and maintainability.

10.4. Configure the node to extract the intent from the structured JSON output using the expression `$.data.intent`.

10.5. Define conditions to determine the next workflow step based on the extracted intent. Since this tutorial considers three possible intent values, two conditions are explicitly tested: `intent == "businessInfo"` and `intent == "orderStatus"`. Any other intent is handled as a default case labeled `Other`.

10.6. To validate the workflow, connect a **Prompt Node** to each possible outcome. Configure each prompt to return a simple, unique response. For example, set the prompt response as `Always respond with "Business Info Response"` for `businessInfo`; `Always respond with "Order Status Response"` for `orderStatus`, and `Always respond with "Other Inquiry Response"` for `Other`.

10.7. Save the modifications and test various inputs to ensure the correct flow execution.

#### Example Test Inputs

**Test Case 1:** Business Information Inquiry

```json
{
  "userInput": "When your company was founded?",
  "orderId": ""
}
```

**Test Case 2:** Order Status Inquiry

```json
{
  "userInput": "Could you provide the status of my order?",
  "orderId": "1099258a-9ae4-4da1-ac1a-0ea516c10210"
}
```

**Test Case 3:** Unrelated Inquiry

```json
{
  "userInput": "Could you list some benefits of adopting a vegan diet?",
  "orderId": ""
}
```

By configuring the conditional node correctly, the workflow can dynamically route user inquiries to the appropriate processing path, ensuring an efficient and structured response handling system.

### Additional Resources

For further understanding of how to access data within objects and define logical expressions in AWS Bedrock Flow, refer to the official documentation:

- **Accessing Data in Objects:** Learn how to reference and extract data from structured JSON objects using AWS Bedrock Flow expressions. [AWS Bedrock Flow Expressions](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-expressions.html?icmpid=docs_bedrock_help_panel_condition_node).
- **Defining Conditions:** Understand how to define logical conditions using relational operators in AWS Bedrock Flow. [Condition Expressions](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html).

---

### Step 11: Configure the Response Node for Knowledge Base

11.1. Open the **AWS Bedrock Console** and access the chatbot workflow.

11.2. Locate the **Prompt Node** handling `intent == "businessInfo"` and remove it.

11.3. In the **Nodes** panel, under **Data**, select **Knowledge Base** and add it to the workflow.

11.4. Rename the node to `NanaSaborNaturalKnowledgeBase` for clarity.

11.5. Select the Knowledge Base created in **Step 3**. If it does not exist, follow this guide to create one: [Setting up Knowledge Bases on AWS Bedrock](https://medium.com/devops-dev/setting-up-knowledge-bases-on-aws-bedrock-with-amazon-s3-and-mongodb-atlas-20d300bd0e38).

11.6. Link the **Knowledge Base Node input** to the **Flow Input Node** to ensure responses reach the user.

11.7. Set the input source to `$.data.userInput` to retrieve relevant content from user queries.

11.8. Choose `Generate responses based on retrieved results` to enable AWS Bedrock to provide structured responses.

11.9. Connect the **Knowledge Base Node** to the **ServiceSelector Condition Node** under the `businessInfo` condition.

11.10. Link the **Knowledge Base Node** to the **Flow Output Node** to ensure responses reach the user.

11.11. Save the workflow and deploy the update.

11.12. Test the setup by submitting business-related queries. See an example of a suitable object for this test:

```json
{
  "userInput": "Nana cookies are lactose-free?",
  "orderId": ""
}
```

By implementing this step, the chatbot dynamically retrieves and generates responses for business-related inquiries, ensuring accuracy and reliability using the AWS Bedrock Knowledge Base.

---

### Step 12: Configuring the Response Node for Order Status Inquiry

#### Step 12.1: Create a Structured Prompt in Prompt Management

To generate well-structured responses for order status inquiries, we will create a dedicated prompt in **Prompt Management**.

##### Steps to Create the Prompt:

12.1.1. Open the **AWS Console**.

12.1.2. Navigate to **Build Tools** → **Prompt Management** → **Create Prompt**. Link to Prompt Management: [here](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/prompt-management)

12.3. Configure the prompt with the following details:
   - **Name:** `OrderStatusResponder`
   - **Description:** `Generates customer-friendly responses for order status inquiries.`

##### System Instructions:

```
Rules:
- The input will be the order status retrieved from a database query.
- Only return a friendly message based on the given status.
- Ensure that the response is in the same language as the user's query.
- Do not provide additional details beyond the order status.
```

##### User Message Format:

```
You are assisting a customer who wants to know the status of their order.
Order Status: {{status}}

Below are example responses for different order statuses. Your response should follow the same structure and tone.

Examples:
- "Processing": "Your order is currently being processed. We will update you once it has been shipped."
- "Shipped": "Great news! Your order has been shipped and is on its way."
- "Delivered": "Your order has been successfully delivered. Enjoy your purchase!"
- "Cancelled": "Unfortunately, your order has been cancelled. If this is unexpected, please contact support."
- "Unknown": "We could not find your order. Please check the order ID and try again."

User language: {{language}}
```

##### Configure Model Execution Parameters

To optimize response quality, adjust the following settings:
- **Model Selection:** Choose an appropriate **Foundation Model** (e.g., **Anthropic Claude, Llama 3, Amazon Titan**).
- **Temperature:** Adjust this value to balance response variability, considering the need for determinism versus randomness.
- **Top-P:** Modify this parameter to control response diversity while maintaining coherence.
- **Response Length:** Set an appropriate limit to ensure responses remain concise and relevant.

#### Step 12.2: Configure the Lambda Node for Order Query

12.2.1. In the **Nodes** panel, under **Code**, select **Lambda** and drag it onto the workflow canvas.

12.2.2. Click on the **Lambda Node** and assign the Lambda function created in **Step 2.3**.

12.2.3. Rename the node to `QueryStatus` for clarity.

12.2.4. Link this Lambda Node to the **Condition Node** that checks for `intent == "orderStatus"`.

12.2.5. Connect the Lambda Node’s input to `Flow Input` and set the input expression to `$.data.orderId`.

#### Step 12.3: Configure the Prompt Node for Order Status Response

12.3.1. Add a **Prompt Node** to the workflow.

12.3.2. Select the structured prompt **OrderStatusResponder** (created in Step 12.1).

12.3.3. Link the output of the **JSONParser Lambda Node** (created in Step 8) to the **Prompt Node** and set `language` as `$.data.language`.

12.3.4. Link the output of the **QueryStatus Lambda Node** (created in Step 12.2) to the **Prompt Node** and set `status` as `$.data`.

12.3.5. Connect the **Prompt Node** to the **Flow Output Node**.

12.3.6. Test the setup by submitting business-related queries. See an example of a suitable object for this test:

```json
{
  "userInput": "Could you provide the status of my order?",
  "orderId": "1099258a-9ae4-4da1-ac1a-0ea516c10210"
}
```

This setup ensures that the order status retrieved from the database is transformed into a well-formatted, customer-friendly response before being presented to the user.

---

### Step 13: Configure the Response Node for General Requests

#### Step 13.1: Create a New Prompt in Prompt Management

To handle general inquiries related to vegan cuisine and dietary restrictions, we will create a specialized prompt in **Prompt Management**. This prompt ensures that responses remain focused on culinary topics and do not cover unrelated or medical subjects.

##### Steps to Create the Prompt:

13.1. Log into the **AWS Console**.

13.2. Navigate to **Build Tools** → **Prompt Management** → **Create Prompt**. Link to Prompt Management: [here](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/prompt-management)

13.3. Configure the new prompt with the following details:
   - **Name:** `VeganDietAssistant`
   - **Description:** `Handles general inquiries about vegan cuisine and dietary restrictions.`

##### Define System Instructions

Under `System Instructions`, enter the following rules:
```
Rules:
- Do not respond to topics that are not related to cuisine and food.
- Do not provide medical advice or treatment recommendations.
- If the user is offensive or asks about an unrelated topic, politely decline to answer.
- If you do not know the answer to a question, apologize and state that you are programmed not to provide responses on that subject.
```

##### Define the User Message Format

Under `User Message`, instruct the AI to focus exclusively on relevant topics:
```
You are an assistant for a vegan bakery. Your goal is to answer customer inquiries related to vegan diets and food options for individuals with gluten, lactose, and egg allergies.

User Input: {{userInput}}
```

##### Configure Model Execution Parameters

To optimize response quality, adjust the following settings:
- **Model Selection:** Choose an appropriate **Foundation Model** (e.g., **Anthropic Claude, Llama 3, Amazon Titan**).
- **Temperature:** Adjust this value to balance response variability, considering the need for determinism versus randomness.
- **Top-P:** Modify this parameter to control response diversity while maintaining coherence.
- **Response Length:** Set an appropriate limit to ensure responses remain concise and relevant.

---

#### Step 13.2: Update the Response Generator Node

Now that the prompt has been created, we will configure the **Response Node** in AWS Bedrock Flows to utilize it.

13.2.1. Open the **AWS Bedrock Console**.

13.2.2. Navigate to **Flows** and locate the existing chatbot flow.

13.2.3. Identify the **Response Node** responsible for handling general inquiries.

13.4. Click on the **Prompt Node** currently being used for responses.

13.2.5. Change the selected prompt to `VeganDietAssistant` (created in Step 13.1).

13.2.6. Ensure input mappings are correctly set:
   - Assign `$.data.userInput` as the input variable.

13.2.7. Save the configuration and deploy the updated flow.

#### Step 13.3:  Test the Updated Workflow

13.3.1. Enter a variety of test inputs related to vegan food and dietary restrictions.

13.3.2. Verify that the responses are informative and aligned with the defined prompt rules.

13.3.3. Enter test inputs that are unrelated (e.g., questions about politics or medicine) and confirm that the assistant declines to respond appropriately.

13.3.4. Test the setup by submitting business-related queries. See an example of a suitable object for this test:

```json
{
  "userInput": "Could you list some benefits of adopting a vegan diet?",
  "orderId": ""
}

```
By implementing this step, the chatbot will now correctly manage general inquiries, ensuring responses remain relevant to vegan cuisine and dietary concerns.

---

## Conclusion

Amazon Bedrock Flows provides a powerful and flexible solution for automating AI-driven workflows. By leveraging a combination of prompt engineering, knowledge bases, AWS Lambda functions, and structured workflow nodes, businesses can build intelligent chatbots capable of handling diverse user inquiries.

This tutorial demonstrated how to create an AI-powered **Order Tracking and Inquiry Chatbot** using AWS Bedrock Flows. We covered:
- **Setting up AWS infrastructure** (DynamoDB for order storage, Lambda functions for processing, and IAM roles for security).
- **Configuring prompt management** to classify and structure responses.
- **Implementing AWS Bedrock Flows** with logical conditions and decision-making nodes.
- **Testing the chatbot** to ensure correct intent classification and output generation.

By following these steps, businesses can integrate similar AI-powered workflows to enhance customer service and automate operations efficiently. This framework can also be extended to handle more complex interactions, such as processing returns, handling complaints, or even providing personalized recommendations.

---

## References

For further exploration, refer to the **Amazon Bedrock Flows Documentation** and experiment with additional integrations such as API calls, analytics tracking, or chatbot personalization based on user history.

- [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/)
- [Amazon Bedrock Flows Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html)
- [Example: Amazon Bedrock Flows Code](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-code-ex.html)
- [Prompt Management Code Example](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-code-ex.html)

---

## Stay Connected

If you found this guide helpful, stay connected for more insights on **AI, cloud security, and AWS automation**:
- **LinkedIn:** [https://www.linkedin.com/in/biagolini](https://www.linkedin.com/in/biagolini)
- **Medium:** [https://medium.com/@biagolini](https://medium.com/@biagolini)
- **GitHub:** [https://github.com/biagolini](https://github.com/biagolini)

Happy building with **AWS Bedrock Flows!** 🚀