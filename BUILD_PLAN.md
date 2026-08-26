# Floci Explorer — Build Plan

## 1. Project Overview

Build a production-quality web application called **Floci Explorer**.

Floci Explorer connects to a running **Floci AWS emulator** and provides a browser-based interface for discovering, inspecting, and visually mapping AWS infrastructure created inside Floci.

The application must:

* Connect to Floci using AWS-compatible APIs.
* Discover AWS resources automatically.
* Display resources grouped by AWS service.
* Display detailed information about resources.
* Build relationships between resources.
* Render infrastructure as an interactive architecture graph.
* Detect infrastructure changes.
* Provide search and filtering.
* Provide raw JSON resource inspection.
* Support additional AWS services through a pluggable collector architecture.
* Eventually support Terraform state as an additional source of infrastructure relationships.

The application must be designed specifically for **Floci**.

Do not assume LocalStack-specific APIs or behavior.

---

# 2. Primary Architecture

```text
                         ┌─────────────────────┐
                         │      Browser        │
                         │                     │
                         │ React + TypeScript  │
                         │ Tailwind CSS        │
                         │ React Flow          │
                         └──────────┬──────────┘
                                    │
                               REST / WS
                                    │
                         ┌──────────▼──────────┐
                         │       FastAPI       │
                         │                     │
                         │ REST API            │
                         │ WebSocket API       │
                         │ Inventory Service   │
                         │ Dependency Engine   │
                         └──────────┬──────────┘
                                    │
                                  boto3
                                    │
                         ┌──────────▼──────────┐
                         │        FLOCI        │
                         │                     │
                         │ 127.0.0.1:4566      │
                         │                     │
                         │ EC2                 │
                         │ S3                  │
                         │ Lambda              │
                         │ DynamoDB            │
                         │ SQS                 │
                         │ SNS                 │
                         │ IAM                 │
                         │ API Gateway         │
                         │ EventBridge         │
                         │ etc.                │
                         └─────────────────────┘
```

---

# 3. Technology Stack

## Backend

* Python 3.12+
* FastAPI
* Uvicorn
* boto3
* Pydantic v2
* httpx
* pytest
* pytest-asyncio
* WebSockets

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* React Flow
* Zustand
* Axios
* React Router
* Lucide React

## Graph Layout

Use:

* ELK.js

or:

* Dagre

Prefer ELK.js when graph complexity becomes significant.

## Development

* Git
* Docker
* Docker Compose

---

# 4. Environment Configuration

Create:

```text
.env
```

Example:

```env
FLOCI_ENDPOINT=http://127.0.0.1:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

FRONTEND_PORT=5173

INVENTORY_REFRESH_INTERVAL=5
```

Create:

```text
.env.example
```

Do not commit `.env`.

---

# 5. Repository Structure

```text
floci-explorer/
│
├── BUILD_PLAN.md
├── CURSOR_PROMPTS.md
├── README.md
├── docker-compose.yml
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── inventory.py
│   │   │   ├── resources.py
│   │   │   ├── graph.py
│   │   │   └── websocket.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── floci/
│   │   │   ├── client.py
│   │   │   ├── connection.py
│   │   │   └── service_registry.py
│   │   │
│   │   ├── collectors/
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── ec2.py
│   │   │   ├── s3.py
│   │   │   ├── lambda_.py
│   │   │   ├── dynamodb.py
│   │   │   ├── sqs.py
│   │   │   ├── sns.py
│   │   │   ├── iam.py
│   │   │   ├── apigateway.py
│   │   │   ├── eventbridge.py
│   │   │   └── stepfunctions.py
│   │   │
│   │   ├── models/
│   │   │   ├── resource.py
│   │   │   ├── relationship.py
│   │   │   ├── graph.py
│   │   │   └── inventory.py
│   │   │
│   │   ├── dependencies/
│   │   │   ├── engine.py
│   │   │   ├── rules.py
│   │   │   └── parsers.py
│   │   │
│   │   └── services/
│   │       ├── inventory_service.py
│   │       ├── resource_service.py
│   │       └── graph_service.py
│   │
│   └── tests/
│       ├── test_health.py
│       ├── test_floci_client.py
│       ├── test_collectors.py
│       ├── test_inventory.py
│       ├── test_resources.py
│       ├── test_dependencies.py
│       └── test_graph.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.js
    │
    └── src/
        ├── main.tsx
        ├── App.tsx
        │
        ├── components/
        │   ├── layout/
        │   ├── dashboard/
        │   ├── graph/
        │   ├── resources/
        │   └── common/
        │
        ├── pages/
        │   ├── Dashboard.tsx
        │   ├── Infrastructure.tsx
        │   ├── Resources.tsx
        │   └── ResourceDetails.tsx
        │
        ├── services/
        │   └── api.ts
        │
        ├── stores/
        │   ├── infrastructure.ts
        │   └── ui.ts
        │
        ├── hooks/
        │   ├── useInventory.ts
        │   ├── useResource.ts
        │   └── useWebSocket.ts
        │
        └── types/
            ├── resource.ts
            ├── relationship.ts
            ├── graph.ts
            └── inventory.ts
```

---

# 6. Backend Architecture

Use:

```text
FastAPI Route
      ↓
Service Layer
      ↓
Collector
      ↓
Floci Client
      ↓
boto3
      ↓
Floci
```

Never put boto3 calls directly inside API route handlers.

---

# 7. Floci Client

Create a centralized client abstraction.

Example:

```python
class FlociClient:
    def get_client(self, service_name: str):
        ...
```

Usage:

```python
ec2 = floci_client.get_client("ec2")
s3 = floci_client.get_client("s3")
lambda_client = floci_client.get_client("lambda")
```

All AWS credentials and endpoint configuration must be centralized.

---

# 8. Universal Resource Model

All AWS resources must be normalized into one common model.

```python
class Resource:
    id: str
    service: str
    resource_type: str
    name: str | None
    arn: str | None
    region: str | None
    status: str | None
    metadata: dict
    raw: dict
```

Example:

```json
{
  "id": "lambda:process-order",
  "service": "lambda",
  "resource_type": "function",
  "name": "process-order",
  "arn": "arn:aws:lambda:...",
  "region": "us-east-1",
  "status": "Active",
  "metadata": {},
  "raw": {}
}
```

---

# 9. Collector Architecture

Create:

```python
class BaseCollector:
    service_name: str

    async def collect(self) -> list[Resource]:
        ...
```

Initial collectors:

* EC2
* S3
* Lambda
* DynamoDB
* SQS
* SNS
* IAM

Later:

* API Gateway
* EventBridge
* Step Functions
* CloudWatch
* KMS
* Secrets Manager
* VPC
* ECS
* ECR
* ALB
* Route53
* CloudFormation

---

# 10. Collector Registry

Create a registry:

```python
COLLECTORS = {
    "ec2": EC2Collector,
    "s3": S3Collector,
    "lambda": LambdaCollector,
    "dynamodb": DynamoDBCollector,
    "sqs": SQSCollector,
    "sns": SNSCollector,
    "iam": IAMCollector,
}
```

Adding a collector must not require changes to unrelated application code.

---

# 11. Inventory API

Implement:

```text
GET /api/health
GET /api/inventory
GET /api/inventory/{service}
```

Example:

```json
{
  "connected": true,
  "timestamp": "2026-08-26T17:00:00Z",
  "services": {
    "ec2": 5,
    "s3": 8,
    "lambda": 12,
    "dynamodb": 3,
    "sqs": 4,
    "sns": 2,
    "iam": 17
  },
  "total_resources": 51
}
```

One collector failure must not cause the entire inventory request to fail.

---

# 12. Resource API

Implement:

```text
GET /api/resources
GET /api/resources/{service}
GET /api/resources/{service}/{resource_id}
```

Support:

```text
?page=1
&page_size=50
&search=
&status=
```

---

# 13. Dependency Engine

Create:

```text
dependencies/
    engine.py
    rules.py
    parsers.py
```

The engine accepts:

```text
List[Resource]
```

and produces:

```text
List[Relationship]
```

Relationship:

```python
class Relationship:
    source: str
    target: str
    relationship: str
    confidence: float
    source_field: str | None
```

---

# 14. Initial Dependency Rules

Implement:

## SQS → Lambda

Use Lambda event source mappings.

```text
SQS ──triggers──> Lambda
```

## SNS → SQS

Use SNS subscriptions.

```text
SNS ──publishes_to──> SQS
```

## Lambda → DynamoDB

Inspect Lambda configuration and environment variables.

Recognize:

```text
TABLE
TABLE_NAME
DYNAMODB_TABLE
DDB_TABLE
```

## Lambda → S3

Recognize:

```text
BUCKET
BUCKET_NAME
S3_BUCKET
S3_BUCKET_NAME
```

## IAM → Lambda

Use Lambda execution role configuration.

## API Gateway → Lambda

Use API Gateway integrations.

## EventBridge → Lambda

Use EventBridge targets.

## Step Functions → Lambda

Parse state machine definitions.

---

# 15. Confidence

Relationships must have confidence.

Examples:

```text
1.0 = direct AWS relationship
0.9 = very strong inference
0.7 = probable inference
0.5 = weak inference
```

The UI should eventually represent inferred relationships differently from confirmed relationships.

---

# 16. Graph API

Implement:

```text
GET /api/graph
```

Response:

```json
{
  "nodes": [],
  "edges": []
}
```

Node:

```json
{
  "id": "lambda:process-order",
  "type": "lambda",
  "data": {
    "label": "process-order",
    "service": "lambda"
  }
}
```

Edge:

```json
{
  "id": "lambda:process-order->dynamodb:orders",
  "source": "lambda:process-order",
  "target": "dynamodb:orders",
  "label": "writes_to"
}
```

---

# 17. Frontend

Use React + TypeScript + Vite.

Use Tailwind for styling.

Use React Flow for the architecture graph.

Use Zustand for global state.

Use Axios for API communication.

---

# 18. UI Layout

Create a dark AWS-console-inspired interface.

```text
┌──────────────────────────────────────────────────────────────┐
│ FLOCI EXPLORER                         ● FLOCI CONNECTED      │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│ Dashboard     │                                              │
│               │                                              │
│ Infrastructure│                CONTENT                       │
│               │                                              │
│ Resources     │                                              │
│               │                                              │
│ EC2       5   │                                              │
│ Lambda   12   │                                              │
│ S3        8   │                                              │
│ DynamoDB  3   │                                              │
│ SQS       4   │                                              │
│ SNS       2   │                                              │
│ IAM      17   │                                              │
│               │                                              │
└───────────────┴──────────────────────────────────────────────┘
```

---

# 19. Dashboard

Show:

* Total resources
* Total services
* Total relationships
* Floci connection status

Service cards:

```text
EC2
5 resources

Lambda
12 resources

S3
8 resources

DynamoDB
3 resources
```

Cards must be clickable.

---

# 20. Infrastructure Graph

Use React Flow.

Support:

* Zoom
* Pan
* Minimap
* Fit view
* Node selection
* Edge selection
* Search
* Service filtering
* Automatic layout
* Reset layout

Create custom nodes for:

* EC2
* S3
* Lambda
* DynamoDB
* SQS
* SNS
* IAM
* API Gateway
* EventBridge
* Step Functions

---

# 21. Resource Explorer

Display:

```text
Service
Name
Type
Status
Region
```

Provide:

* Search
* Service filter
* Status filter
* Pagination

Clicking a resource opens its details.

---

# 22. Resource Details

Display:

* Resource name
* Service
* Type
* ARN
* Region
* Status
* Metadata
* Dependencies
* Dependents
* Raw JSON

---

# 23. Connection Status

Display:

```text
● FLOCI CONNECTED
```

or:

```text
● FLOCI DISCONNECTED
```

Show:

* Endpoint
* Region
* Last successful check

Provide:

```text
Reconnect
```

button.

---

# 24. Real-Time Updates

Start with polling.

Default:

```text
5 seconds
```

Process:

```text
GET /api/inventory
        ↓
compare with previous state
        ↓
update UI
```

Later add:

```text
/ws/infrastructure
```

Events:

```json
{
  "event": "resource_created",
  "resource": {}
}
```

```json
{
  "event": "resource_updated",
  "resource": {}
}
```

```json
{
  "event": "resource_deleted",
  "resource_id": "..."
}
```

---

# 25. Error Handling

Individual service failures must be isolated.

Example:

```text
EC2        ✓
S3         ✓
Lambda     ✓
DynamoDB   ✓
SQS        ✗
SNS        ✓
```

The application must remain usable.

---

# 26. Testing

Use pytest.

Test:

* Floci connection
* collectors
* inventory
* resources
* dependency rules
* graph generation
* API endpoints

Unit tests must mock boto3.

Do not require live Floci for unit tests.

---

# 27. Docker

Provide Dockerfiles for:

* backend
* frontend

Provide:

```text
docker-compose.yml
```

The application must support both:

1. Floci running locally.

```text
FLOCI_ENDPOINT=http://127.0.0.1:4566
```

2. Floci running inside Docker.

The exact Floci image/configuration must not be hardcoded unless confirmed by the user.

---

# 28. Development Phases

## Phase 1 — Backend Foundation

Implement:

* configuration
* logging
* Floci client
* health endpoint
* EC2 collector
* S3 collector
* Lambda collector
* inventory endpoint

Stop and test.

---

## Phase 2 — More Collectors

Implement:

* DynamoDB
* SQS
* SNS
* IAM

Then resource API.

Stop and test.

---

## Phase 3 — Dependency Engine

Implement:

* Lambda → DynamoDB
* Lambda → S3
* SQS → Lambda
* SNS → SQS
* IAM → Lambda

Then graph API.

Stop and test.

---

## Phase 4 — Frontend Foundation

Implement:

* Vite
* React
* Tailwind
* routing
* layout
* sidebar
* top bar
* API service

---

## Phase 5 — Dashboard

Implement:

* resource counters
* service cards
* connection status
* refresh

---

## Phase 6 — Resource Explorer

Implement:

* resource list
* search
* filtering
* resource details
* raw JSON viewer

---

## Phase 7 — Architecture Graph

Implement:

* React Flow
* custom AWS nodes
* edges
* automatic layout
* filters
* minimap
* zoom
* fit view

---

## Phase 8 — Real-Time

Implement:

* polling
* change detection
* WebSockets

---

## Phase 9 — More AWS Services

Add collectors incrementally.

---

# 29. Future Terraform Integration

Eventually support:

```text
terraform.tfstate
```

as a second source of infrastructure information.

Architecture:

```text
                    ┌───────────────┐
                    │     Floci     │
                    │ Runtime State │
                    └───────┬───────┘
                            │
                          boto3
                            │
                            ▼
                    ┌───────────────┐
                    │   Inventory   │
                    └───────┬───────┘
                            │
                            │
              ┌─────────────┴──────────────┐
              │                            │
              ▼                            ▼
      Runtime relationships         terraform.tfstate
              │                            │
              └─────────────┬──────────────┘
                            ▼
                    ┌───────────────┐
                    │  Dependency   │
                    │    Engine     │
                    └───────┬───────┘
                            ▼
                    Architecture Graph
```

Terraform state should NOT be required for the first version.

---

# 30. Quality Requirements

Cursor must:

* Keep backend and frontend independent.
* Use type hints.
* Avoid duplicated code.
* Use dependency injection where appropriate.
* Use Pydantic models.
* Use meaningful exceptions.
* Use structured logging.
* Add tests with new features.
* Keep AWS SDK logic inside collectors.
* Never hardcode resource names.
* Never hardcode relationships.
* Never assume a specific AWS account ID.
* Never assume LocalStack.
* Handle unsupported services gracefully.
* Keep UI responsive.
* Keep graph rendering performant.
* Avoid huge components.
* Break UI into reusable components.

---

# 31. Definition of Done

The first production milestone is complete when:

1. Floci is running on port 4566.
2. Backend successfully connects to Floci.
3. EC2/S3/Lambda resources are discovered.
4. Dashboard displays counts.
5. Resource explorer displays resources.
6. Resource details are viewable.
7. Graph displays resources.
8. Graph displays detected relationships.
9. Search works.
10. Service filtering works.
11. Floci connection status works.
12. Refresh works.
13. Tests pass.
14. README contains setup instructions.

Only after this milestone should additional AWS services be implemented.
