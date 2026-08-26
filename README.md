# Floci Explorer

Browser-based explorer for AWS infrastructure running inside **Floci**.

This is Floci, not LocalStack. The backend uses AWS-compatible boto3 calls against `FLOCI_ENDPOINT`.

## Prerequisites

- Python 3.12+
- Node.js 20+
- Floci emulator (default `http://127.0.0.1:4566`)

## Configuration

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|---|---|---|
| `FLOCI_ENDPOINT` | `http://127.0.0.1:4566` | Floci AWS endpoint for **local** Python/Node |
| `FLOCI_DOCKER_ENDPOINT` | `http://floci:4566` | Floci URL used **inside Docker Compose** |
| `AWS_REGION` | `us-east-1` | Region sent to boto3 |
| `AWS_ACCESS_KEY_ID` | `test` | Access key (emulator) |
| `AWS_SECRET_ACCESS_KEY` | `test` | Secret key (never logged) |
| `INVENTORY_REFRESH_INTERVAL` | `5` | UI polling interval (seconds) |
| `SHOW_SECRETS` | `false` | Unmask env vars globally |
| `CORS_ORIGINS` | Vite origin | Allowed browser origins |

Do not commit `.env`.

## Start Floci

Run your Floci emulator so it listens on port 4566 (or set `FLOCI_ENDPOINT`). This repo does not ship a Floci image.

## Start backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` and `/ws` to the backend.

## Docker

One image serves the UI and API on port 8000.

```bash
docker build -t floci-explorer .
docker run --rm -p 8000:8000 --add-host host.docker.internal:host-gateway ^
  -e FLOCI_ENDPOINT=http://host.docker.internal:4566 ^
  floci-explorer
```

On Linux/macOS use `\` instead of `^`. Open `http://127.0.0.1:8000`.

Or:

```bash
docker compose up --build
```

The image talks to Floci on the Docker network at `http://floci:4566` (container name `floci` / `floci_aws_main`). Do not set `FLOCI_ENDPOINT=http://127.0.0.1:4566` in Compose: inside a container that is not your host.

If Floci is not on the `floci_default` network, set `FLOCI_DOCKER_ENDPOINT` and attach Explorer to Floci's network. Binding Floci to `127.0.0.1:4566` only is fine for host clients; other containers should use the Floci service name, not localhost.

## API

- `GET /api/health`
- `POST /api/health/reconnect`
- `GET /api/inventory`
- `GET /api/inventory/{service}`
- `GET /api/resources`
- `GET /api/resources/{service}`
- `GET /api/resources/{service}/{resource_id}`
- `GET /api/graph`
- `WS /ws/infrastructure`
- `POST /api/terraform/analyze` (optional `terraform.tfstate`)

Floci emulates about 75 AWS services. Explorer registers a collector for each matrix service:

- Specialized collectors (rich metadata): EC2, S3, Lambda, DynamoDB, SQS, SNS, IAM, API Gateway, EventBridge, Step Functions, CloudWatch Logs, KMS, Secrets Manager, VPC, ECS, ECR, ELB v2, Route 53, CloudFormation, STS.
- Generic list collectors for the rest of the [Floci service matrix](https://floci.io/floci/services/).
- Presence-only entries for APIs with no inventory list (Sign-In, Bedrock Runtime, Pricing, Cost Explorer, RDS Data API, and similar). These show as 0 resources and are never faked.

If Floci or boto3 does not implement a list API, the collector is marked unsupported.

## Adding a collector

1. Create `backend/app/collectors/<service>.py` extending `BaseCollector`.
2. Return `list[Resource]` from `collect_sync`.
3. Register the class in `backend/app/collectors/registry.py`.
4. Add unit tests with a mocked boto3 client.
5. If Floci does not implement the API, catch `ClientError` and set `self.supported = False`. Do not invent resources.

## Adding a dependency rule

1. Add a function in `backend/app/dependencies/rules.py`.
2. Accept `list[Resource]` plus the lookup index.
3. Emit `Relationship` only when both ends exist.
4. Set `confidence` (`1.0` direct, `< 0.9` inferred).
5. Append the function to `RULES`.

## Terraform integration

Terraform state is optional. Upload `terraform.tfstate` on the Terraform page. The parser is read-only and never writes the file. Drift is classified as `MATCH`, `MISSING_IN_FLOCI`, `MISSING_IN_TERRAFORM`, or `DIFFERENT_CONFIGURATION`.

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```
