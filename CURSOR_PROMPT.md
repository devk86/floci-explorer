# Floci Explorer — Cursor Build Prompts

These prompts are designed to be executed sequentially in Cursor.

**Important:** Do not give Cursor all prompts at once.

Complete one phase, test it, fix problems, then move to the next prompt.

---

# Prompt 00 — Project Initialization

```text
Read BUILD_PLAN.md completely before making any changes.

We are building "Floci Explorer", a web application for visualizing AWS infrastructure running inside FLOCI.

IMPORTANT:

This is FLOCI, not LocalStack.

Do not assume LocalStack APIs or implementation details.

Your job in this step is ONLY to initialize the project.

Create the repository structure described in BUILD_PLAN.md.

Create:

backend/
frontend/
README.md
.gitignore
.env.example
docker-compose.yml

Do not implement application functionality yet.

Backend should be prepared for:

Python 3.12+
FastAPI
boto3
Pydantic v2
pytest
pytest-asyncio

Frontend should be prepared for:

React
TypeScript
Vite
Tailwind CSS
React Flow
Zustand
Axios
React Router
Lucide React

Do not over-engineer the project.

At the end:

1. Show the directory tree.
2. Show backend requirements.
3. Show frontend dependencies.
4. Provide exact commands to install dependencies.
5. Verify the project structure.

Do not start Phase 1 functionality yet.
```

---

# Prompt 01 — Backend Foundation

```text
Read BUILD_PLAN.md.

Implement PHASE 1 only.

Do not implement frontend functionality.

Create the backend foundation.

Requirements:

1. Configuration

Create:

backend/app/core/config.py

Use Pydantic settings.

Environment variables:

FLOCI_ENDPOINT=http://127.0.0.1:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

2. Logging

Create centralized application logging.

3. Floci client

Create:

backend/app/floci/client.py

Implement a FlociClient abstraction around boto3.

It must support:

get_client("ec2")
get_client("s3")
get_client("lambda")

Do not duplicate boto3 configuration.

4. Connection manager

Create:

backend/app/floci/connection.py

Implement:

- connectivity check
- connection status
- last successful connection time

5. Health API

Create:

GET /api/health

Return:

{
  "status": "ok",
  "floci_connected": true
}

6. FastAPI application

Create:

backend/app/main.py

Use routers.

7. Tests

Create tests for:

- configuration
- Floci client
- health endpoint

IMPORTANT:

Do not implement EC2/S3/Lambda collectors yet.

Run pytest.

Fix all errors.

At the end provide:

- files created
- commands to run
- pytest result
- curl command for /api/health
```

---

# Prompt 02 — EC2/S3/Lambda Collectors

```text
Read BUILD_PLAN.md.

Implement the first three collectors:

EC2
S3
Lambda

Use the BaseCollector architecture.

Create:

collectors/base.py
collectors/registry.py
collectors/ec2.py
collectors/s3.py
collectors/lambda_.py

Create the universal Resource Pydantic model.

Every collector must return:

list[Resource]

Resource must contain:

id
service
resource_type
name
arn
region
status
metadata
raw

Requirements:

EC2:

Use boto3 describe_instances.

Flatten EC2 instances into Resource objects.

S3:

Use list_buckets.

Lambda:

Use list_functions.

Do not expose raw boto3 response directly through the API.

Normalize resources.

Handle pagination where appropriate.

Handle AWS/Floci errors gracefully.

Add unit tests using mocked boto3 clients.

Do not implement DynamoDB, SQS, SNS, IAM yet.

Run pytest.

Fix all failures.

At the end show sample normalized Resource output for:

one EC2 instance
one S3 bucket
one Lambda function
```

---

# Prompt 03 — Inventory API

```text
Read BUILD_PLAN.md.

Implement the inventory service.

Create:

services/inventory_service.py
api/inventory.py
models/inventory.py

Implement:

GET /api/inventory

It must run all registered collectors.

Important:

If one collector fails, other collectors must still be processed.

For example:

EC2 ✓
S3 ✓
Lambda ✗

The API must still return EC2 and S3 results.

Return:

{
  "connected": true,
  "timestamp": "...",
  "services": {
    "ec2": 5,
    "s3": 3,
    "lambda": 12
  },
  "total_resources": 20,
  "errors": []
}

Also implement:

GET /api/inventory/{service}

Return resources for the requested service.

Add tests.

Do not implement the frontend.

Do not implement dependency relationships yet.

Run pytest and fix all failures.
```

---

# Prompt 04 — DynamoDB/SQS/SNS/IAM

```text
Read BUILD_PLAN.md.

Implement PHASE 2 collectors.

Add:

DynamoDB
SQS
SNS
IAM

Create:

dynamodb.py
sqs.py
sns.py
iam.py

Register all collectors.

Follow the same BaseCollector architecture.

Important:

Do not duplicate code.

Each collector must normalize AWS responses into Resource objects.

DynamoDB:

Discover tables.

SQS:

Discover queues.

SNS:

Discover topics and relevant subscription information.

IAM:

Discover roles and policies where supported by Floci.

Handle pagination.

Handle missing APIs gracefully.

Do not let one collector failure break inventory.

Add unit tests with mocked boto3 clients.

Update the inventory tests.

Run the complete backend test suite.

Do not modify the frontend.
```

---

# Prompt 05 — Resource API

```text
Read BUILD_PLAN.md.

Implement the resource API.

Create:

services/resource_service.py
api/resources.py

Implement:

GET /api/resources

GET /api/resources/{service}

GET /api/resources/{service}/{resource_id}

Support query parameters:

page
page_size
search
status

Examples:

/api/resources?page=1&page_size=50

/api/resources/lambda

/api/resources/lambda?search=order

/api/resources/ec2?status=running

Requirements:

- case-insensitive search
- pagination
- service filtering
- status filtering
- normalized Resource output
- proper 404 handling
- proper validation

Do not return raw boto3 responses as the primary API structure.

Keep raw resource JSON available inside the Resource model.

Add tests.

Run pytest.
```

---

# Prompt 06 — Dependency Engine

```text
Read BUILD_PLAN.md.

Now implement the dependency engine.

Do not modify the frontend.

Create:

dependencies/engine.py
dependencies/rules.py
dependencies/parsers.py
models/relationship.py

The dependency engine must accept:

list[Resource]

and produce:

list[Relationship]

Relationship:

source
target
relationship
confidence
source_field

Implement these rules:

1. SQS -> Lambda

Use Lambda event source mappings.

Relationship:

triggers

2. SNS -> SQS

Use SNS subscriptions.

Relationship:

publishes_to

3. Lambda -> DynamoDB

Inspect Lambda environment variables.

Recognize:

TABLE
TABLE_NAME
DYNAMODB_TABLE
DDB_TABLE

Relationship:

reads_from_or_writes_to

Do not claim write/read direction unless it can be established.

4. Lambda -> S3

Recognize:

BUCKET
BUCKET_NAME
S3_BUCKET
S3_BUCKET_NAME

5. IAM Role -> Lambda

Use Lambda execution role.

Relationship:

execution_role

6. API Gateway -> Lambda

Prepare the architecture for this rule even if API Gateway collector
does not exist yet.

7. EventBridge -> Lambda

Prepare the architecture for this rule.

8. Step Functions -> Lambda

Prepare the architecture for this rule.

Important:

Do not create false relationships.

Only create a relationship when there is sufficient evidence.

Add confidence values.

Add comprehensive unit tests.

Use synthetic Resource objects for tests.

Run pytest.
```

---

# Prompt 07 — Graph API

```text
Read BUILD_PLAN.md.

Implement the graph service and graph API.

Create:

services/graph_service.py
api/graph.py
models/graph.py

Implement:

GET /api/graph

The graph service must:

1. Obtain current resources.
2. Run DependencyEngine.
3. Convert resources into graph nodes.
4. Convert relationships into graph edges.

Node:

{
  "id": "...",
  "type": "...",
  "data": {
    "label": "...",
    "service": "...",
    "resource_type": "..."
  }
}

Edge:

{
  "id": "...",
  "source": "...",
  "target": "...",
  "label": "...",
  "data": {
    "confidence": 0.9
  }
}

Do not add React-specific assumptions to backend business logic.

Add tests.

Test:

- graph with no resources
- graph with one resource
- graph with multiple resources
- graph with relationships
- graph with failed collector

Run pytest.
```

---

# Prompt 08 — Frontend Foundation

```text
Read BUILD_PLAN.md.

Now implement PHASE 4.

Build the React frontend.

Use:

React
TypeScript
Vite
Tailwind CSS
React Router
Zustand
Axios
Lucide React

Create:

App.tsx
routing
layout
sidebar
top navigation
API service
global stores

Pages:

Dashboard
Infrastructure
Resources
ResourceDetails

Create a dark AWS-console-inspired UI.

Requirements:

- responsive layout
- left sidebar
- top navigation
- connection status indicator
- clean typography
- reusable components
- no hardcoded infrastructure data

Create frontend TypeScript types matching backend models.

Create:

services/api.ts

API methods:

getHealth()
getInventory()
getResources()
getResource()
getGraph()

Do not implement React Flow yet.

Do not implement real-time updates yet.

Use mocked frontend data ONLY if required to make the UI render,
but clearly isolate mocks and prepare the code to replace them
with the backend APIs.

Run npm build and fix all TypeScript errors.
```

---

# Prompt 09 — Connect Dashboard to Backend

```text
Read BUILD_PLAN.md.

Connect the React dashboard to the real FastAPI backend.

Do not use mock data.

Dashboard must call:

GET /api/health
GET /api/inventory

Display:

Total Resources
Total Services
Total Relationships
Floci Status

Display service cards:

EC2
S3
Lambda
DynamoDB
SQS
SNS
IAM

Each card must show resource count.

Clicking a service card must navigate to:

/resources?service=<service>

Add:

loading states
error states
empty states

Connection indicator:

CONNECTED
DISCONNECTED

Add refresh button.

Use clean reusable components.

Run frontend build.

Fix all errors.
```

---

# Prompt 10 — Resource Explorer

```text
Read BUILD_PLAN.md.

Implement the Resources page.

Requirements:

Search box.

Service filter.

Status filter.

Pagination.

Table columns:

Service
Name
Type
Status
Region

Clicking a row navigates to:

/resources/:service/:resourceId

Resource details must display:

Name
Service
Type
ARN
Region
Status
Metadata
Relationships
Raw JSON

Raw JSON must be formatted and readable.

Implement loading, error, and empty states.

Do not duplicate API logic.

Use the centralized API service.

Run TypeScript build and fix all errors.
```

---

# Prompt 11 — React Flow Infrastructure Graph

```text
Read BUILD_PLAN.md.

Implement the Infrastructure page using React Flow.

Call:

GET /api/graph

Render:

nodes
edges

Create custom node components for:

EC2
S3
Lambda
DynamoDB
SQS
SNS
IAM

Each node should show:

AWS service icon
resource name
resource type

Support:

zoom
pan
minimap
fit view
node selection
edge selection
search
service filtering

Add automatic graph layout using ELK.js or Dagre.

Do not put all graph logic into one component.

Create reusable:

GraphCanvas
ResourceNode
ServiceNode
GraphToolbar
GraphFilters

Clicking a node must open the resource details.

The graph must handle:

0 nodes
1 node
many nodes
disconnected nodes
large graphs

Do not crash if an edge references a missing node.

Run frontend build.
```

---

# Prompt 12 — Graph UX

```text
Improve the infrastructure graph UX.

Requirements:

1. Search resources.

2. Filter by AWS service.

3. Toggle relationship visibility.

4. Fit graph to screen.

5. Reset layout.

6. Zoom controls.

7. Minimap.

8. Show relationship labels.

9. Show inferred relationships differently from confirmed relationships.

Use confidence:

>= 0.9 confirmed-looking relationship
< 0.9 inferred-looking relationship

Do not use misleading visuals that imply certainty where there is only inference.

When a node is selected:

- highlight connected nodes
- highlight connected edges
- dim unrelated nodes

Keep performance reasonable for hundreds of nodes.
```

---

# Prompt 13 — Resource Details UX

```text
Improve Resource Details.

Create a professional inspector panel/page.

Sections:

Overview
Configuration
Relationships
Metadata
Raw JSON

For Lambda show when available:

Runtime
Handler
Memory
Timeout
Role
Environment variables

For EC2 show when available:

Instance ID
Instance type
State
AMI
Subnet
Security groups
Private IP
Public IP
Tags

For S3 show:

Bucket name
Region
Creation date
Tags if available

For DynamoDB show:

Table name
Status
Partition key
Sort key
Billing mode if available

For SQS show:

Queue URL
Queue ARN
Attributes

For SNS show:

Topic ARN
Subscriptions

Do not assume every field exists.

Only render fields returned by the backend.

Use reusable field/value components.
```

---

# Prompt 14 — Polling and Live Updates

```text
Read BUILD_PLAN.md.

Implement infrastructure refresh.

Initially use polling.

Default interval:

5 seconds

Create:

useInventory()
useWebSocket()

On each refresh:

1. Fetch inventory.
2. Detect whether resource counts changed.
3. Refresh graph when required.
4. Refresh visible resource list if required.

Do not constantly reload the entire React application.

Add:

Pause refresh
Resume refresh
Refresh now

Show:

Last updated: HH:MM:SS

Avoid race conditions.

Prevent overlapping requests.

Handle backend disconnection gracefully.
```

---

# Prompt 15 — WebSocket Support

```text
Implement WebSocket infrastructure updates.

Backend:

/ws/infrastructure

Support events:

resource_created
resource_updated
resource_deleted
inventory_changed

Frontend should connect automatically.

If WebSocket disconnects:

- attempt reconnect
- use exponential backoff
- do not flood the backend

When an event is received:

update relevant Zustand state
refresh affected resource
refresh graph when necessary

Polling should remain available as fallback.

Do not make WebSockets mandatory for the application to function.
```

---

# Prompt 16 — API Gateway/EventBridge/Step Functions

```text
Read BUILD_PLAN.md.

Add collectors for:

API Gateway
EventBridge
Step Functions

Follow the existing collector architecture.

Do not change existing collectors unnecessarily.

Implement relationships:

API Gateway -> Lambda
EventBridge -> Lambda
Step Functions -> Lambda

Use direct AWS configuration relationships wherever available.

Add unit tests.

Update graph tests.

Update README.

Run the full backend test suite.
```

---

# Prompt 17 — Additional AWS Services

```text
Read BUILD_PLAN.md.

Expand Floci Explorer service support.

Before implementing each service:

1. Verify that the required AWS APIs are supported by the current
Floci version.
2. If an API is not supported, gracefully mark the service as
unsupported.
3. Do not fake resource data.

Prioritize:

CloudWatch
KMS
Secrets Manager
VPC
Subnets
Security Groups
ECS
ECR
ALB
Route53
CloudFormation

For each service:

- collector
- normalized Resource
- tests
- UI icon/node
- resource details
- relationships where possible

Do not modify unrelated functionality.
```

---

# Prompt 18 — Terraform State Integration

```text
Read BUILD_PLAN.md.

Now add optional Terraform state integration.

The application should optionally accept:

terraform.tfstate

Do NOT require Terraform state for normal Floci operation.

Create a Terraform state parser.

Extract:

resource addresses
resource types
resource names
resource instances
references/dependencies where available

Normalize Terraform resources into the same internal representation
used by Floci resources.

Create a reconciliation layer:

Floci runtime resource
        +
Terraform state resource
        =
Unified resource

Show in the UI whether a resource is:

Floci only
Terraform only
Matched

Do not destroy or modify Terraform state.

Read-only only.

Add tests.
```

---

# Prompt 19 — Infrastructure Drift Detection

```text
Using the Terraform integration, implement optional drift detection.

Compare:

Terraform desired/state information

against:

Floci runtime information

Classify:

MATCH
MISSING_IN_FLOCI
MISSING_IN_TERRAFORM
DIFFERENT_CONFIGURATION

Display drift in the UI.

Example:

Lambda process-order

Terraform:
memory = 512

Floci:
memory = 1024

Status:

DRIFT DETECTED

Do not attempt to automatically fix drift.

This is read-only analysis.
```

---

# Prompt 20 — Performance Optimization

```text
Review the complete application.

Optimize for:

500+ resources
1000+ relationships

Backend:

- avoid unnecessary boto3 calls
- use pagination
- cache short-lived inventory data
- parallelize independent collectors where safe

Frontend:

- memoize expensive components
- avoid unnecessary graph re-renders
- avoid rebuilding graph layout unnecessarily
- virtualize large resource tables if necessary

Do not prematurely introduce Redis or a database.

Measure before optimizing.

Keep behavior unchanged.
```

---

# Prompt 21 — Security Review

```text
Perform a security review.

Check:

- CORS
- environment variables
- credentials
- API exposure
- WebSocket exposure
- XSS
- raw JSON rendering
- user-controlled search parameters
- logging of secrets
- Lambda environment variable display
- Docker configuration

IMPORTANT:

Never log:

AWS_SECRET_ACCESS_KEY
secret values
passwords
tokens
API keys

Mask sensitive values in the UI.

For environment variables, support:

SHOW SECRETS

default:

false

When false, values must be masked.

Do not expose secrets unnecessarily.
```

---

# Prompt 22 — Production Readiness

```text
Perform a complete production-readiness review.

Check:

Backend:
- typing
- error handling
- logging
- tests
- API documentation
- configuration

Frontend:
- TypeScript errors
- loading states
- error states
- empty states
- responsive layout
- graph performance
- accessibility

Infrastructure:
- Dockerfiles
- docker-compose
- environment configuration
- health checks

Documentation:

README.md must explain:

installation
configuration
starting Floci
starting backend
starting frontend
Docker
API
adding collectors
adding dependency rules
Terraform integration

Run:

backend tests
frontend build

Fix all errors.

Do not add unnecessary dependencies.
```

---

# Prompt 23 — Final Code Review

```text
Act as a senior Python + React engineer.

Review the entire Floci Explorer codebase.

Do not rewrite working code unnecessarily.

Look specifically for:

- duplicated logic
- circular dependencies
- overly large classes
- overly large React components
- missing error handling
- incorrect async usage
- boto3 clients created unnecessarily
- memory leaks
- WebSocket reconnect problems
- React rendering loops
- graph performance problems
- missing tests
- incorrect TypeScript types
- hardcoded AWS assumptions
- LocalStack-specific assumptions
- Floci-specific compatibility issues

For every problem:

1. Explain the issue.
2. Fix it.
3. Add/update tests if required.

After completion:

Run the complete test suite.

Run the frontend production build.

Provide a final summary of changes.
```

---

# Prompt 24 — UI Polish

```text
Polish the Floci Explorer UI.

The application should feel like a professional developer/cloud
engineering tool rather than a generic CRUD dashboard.

Design goals:

- dark AWS-console-inspired interface
- clean spacing
- subtle borders
- readable typography
- compact infrastructure cards
- clear service icons
- professional resource tables
- polished graph nodes
- clear connection status
- responsive layout

Add:

- keyboard-friendly search
- tooltips
- loading skeletons
- empty states
- error states
- toast notifications where appropriate

Do not sacrifice performance.

Do not change backend behavior.
```

---

# Recommended Cursor Workflow

Use the prompts in this order:

```text
00 Project Initialization
        ↓
01 Backend Foundation
        ↓
02 Collectors
        ↓
03 Inventory API
        ↓
04 More Collectors
        ↓
05 Resource API
        ↓
06 Dependency Engine
        ↓
07 Graph API
        ↓
08 Frontend Foundation
        ↓
09 Dashboard
        ↓
10 Resource Explorer
        ↓
11 React Flow
        ↓
12 Graph UX
        ↓
13 Resource Details
        ↓
14 Polling
        ↓
15 WebSockets
        ↓
16 API Gateway/EventBridge/Step Functions
        ↓
17 Additional Services
        ↓
18 Terraform Integration
        ↓
19 Drift Detection
        ↓
20 Performance
        ↓
21 Security
        ↓
22 Production Readiness
        ↓
23 Final Review
        ↓
24 UI Polish
```

# Important Cursor Rule

After each prompt, **do not immediately move to the next prompt**.

Use this cycle:

```text
Implement
   ↓
Run tests
   ↓
Run application
   ↓
Verify manually
   ↓
Fix errors
   ↓
Commit to Git
   ↓
Next phase
```

Recommended Git checkpoints:

```text
phase-01-backend-foundation
phase-02-collectors
phase-03-inventory
phase-04-resource-api
phase-05-dependency-engine
phase-06-graph-api
phase-07-frontend
phase-08-dashboard
phase-09-resource-explorer
phase-10-infrastructure-graph
phase-11-realtime
phase-12-additional-services
phase-13-terraform
phase-14-drift-detection
phase-15-production
```
