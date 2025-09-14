import anthropic
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def normalize_component_types(adjacency_json_str: str) -> dict:
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    retries = 0
    while retries < 5:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20000,
            temperature=1,
            system="# Graph Component Categorizer System Prompt\n\nYou are a specialized system that categorizes graph vertices representing software components into standardized component types. Your task is to take a JSON adjacency list with natural language vertex names and convert them into a standardized format.\n\n## Supported Components\nYou must categorize each vertex into exactly one of these six component types:\n- `react-frontend` - Frontend applications, web interfaces, client-side components\n- `flask-backend` - Backend services, APIs, server applications, business logic\n- `nginx` - Reverse proxies, load balancers, web servers, gateways\n- `mysql` - Databases, data storage, persistent storage systems\n- `redis` - Cache systems, in-memory datastores, session stores\n- `rabbitmq` - Message queues, message brokers, asynchronous task queues, pub/sub systems\n\n## Input Format\nYou will receive a JSON adjacency list where:\n- Keys are vertex names in natural language\n- Values are arrays of connected vertex names\n\nExample input:\n```json\n{\"Frontend\": [\"Proxy\"], \"Proxy\": [\"Backend\", \"Frontend\"], \"Backend\": [\"Proxy\", \"SQL Database\", \"Cache\", \"Message Queue\"], \"SQL Database\": [\"Backend\"], \"Cache\": [\"Backend\"], \"Message Queue\": [\"Backend\"]}\n```\n\n## Categorization Guidelines\n- **Frontend/UI/Client/Web App** → `react-frontend`\n- **Backend/API/Server/Service** → `flask-backend` \n- **Proxy/Load Balancer/Gateway/Web Server** → `nginx`\n- **Database/Storage/Data/SQL** → `mysql`\n- **Cache/Redis/Memory Store/Session Store** → `redis`\n- **Message Queue/Queue/Broker/RabbitMQ/Pub/Sub/Task Queue/Worker Queue** → `rabbitmq`\n\n## JSON Schema\nYour output must strictly conform to this JSON schema:\n\n```json\n{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"patternProperties\": {\n    \"^(react-frontend|flask-backend|nginx|mysql|redis|rabbitmq)$\": {\n      \"type\": \"array\",\n      \"items\": {\n        \"type\": \"string\",\n        \"enum\": [\"react-frontend\", \"flask-backend\", \"nginx\", \"mysql\", \"redis\", \"rabbitmq\"]\n      },\n      \"uniqueItems\": true\n    }\n  },\n  \"additionalProperties\": false,\n  \"minProperties\": 1\n}\n```\n\n## Output Requirements\n1. **JSON Format Only**: Return only a valid JSON adjacency list that conforms to the schema\n2. **Valid Keys**: All object keys must be one of: `react-frontend`, `flask-backend`, `nginx`, `mysql`, `redis`, `rabbitmq`\n3. **Valid Values**: All array elements must be one of: `react-frontend`, `flask-backend`, `nginx`, `mysql`, `redis`, `rabbitmq`\n4. **No Duplicates**: Each array must contain unique elements (no duplicate connections)\n5. **Preserve Structure**: Maintain the same graph connectivity structure\n6. **Consistent Mapping**: If a natural language term appears multiple times, always map it to the same standardized component\n\n## Output Format Example\n```json\n{\"react-frontend\": [\"nginx\"], \"nginx\": [\"flask-backend\", \"react-frontend\"], \"flask-backend\": [\"nginx\", \"mysql\", \"redis\", \"rabbitmq\"], \"mysql\": [\"flask-backend\"], \"redis\": [\"flask-backend\"], \"rabbitmq\": [\"flask-backend\"]}\n```\n\n## Instructions\n1. Analyze each vertex name in the input\n2. Categorize it into one of the six supported components based on its likely function\n3. Replace the vertex name with the standardized name throughout the adjacency list\n4. Ensure all connections are preserved with the new names\n5. Return only the JSON adjacency list, no additional text or explanation",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": adjacency_json_str
                        }
                    ]
                }
            ]
        )

        try:
            if isinstance(message.content, list) and len(message.content) > 0 and message.content[0].text:
                res = {}
                cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", message.content[0].text.strip(), flags=re.DOTALL)
                normalized_components = json.loads(cleaned_text)
                res["success"] = True
                res["components"] = normalized_components
                return res
            else:
                retries += 1
                print("===", "Message content not in expected format:", message.content, "===\n")
                
        except json.JSONDecodeError as e:
            retries += 1
            print("===", "Exception occured while converting to JSON:", e, "===\n")
            print(message.content[0].text)
            
        except Exception as e:
            print(f"!!! Unknown exception occured: {e} !!!")
            return {"success": False}

    return {"success": False}