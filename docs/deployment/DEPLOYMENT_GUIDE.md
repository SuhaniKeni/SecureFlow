# SecureFlow: Production Container Deployment Guide (Stage 5.19)

This guide documents exact instructions for containerizing and deploying SecureFlow using Docker, Docker Compose, environment configuration, and health check monitoring.

---

## 1. Environment Configuration Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### `.env` File Parameters:
* `ENVIRONMENT`: Set to `production` or `development`.
* `DATABASE_URL`: `sqlite:///./data/secureflow.db` (local synthetic SQLite instance).
* `API_PORT`: `8000` (FastAPI backend service port).
* `MODEL_DIR`: `secureflow/models` (pre-trained scikit-learn model payloads).

---

## 2. Docker Container Build & Execution

To build and start all SecureFlow containers in detached mode:

```bash
docker compose up --build -d
```

### Verifying Container Status & Health Checks:
```bash
docker compose ps
```

Expected Output:
```text
NAME                  IMAGE                COMMAND                  SERVICE    CREATED          STATUS                    PORTS
secureflow-backend    secureflow-backend   "uvicorn secureflow.…"   backend    10 seconds ago   Up 10 seconds (healthy)   0.0.0.0:8000->8000/tcp
secureflow-frontend   secureflow-frontend  "/docker-entrypoint.…"   frontend   10 seconds ago   Up 10 seconds (healthy)   0.0.0.0:80->80/tcp, 0.0.0.0:3000->80/tcp
```

---

## 3. Container Services & Health Endpoints

| Service | Port Mapping | Container Healthcheck Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Backend API** | `http://localhost:8000` | `http://localhost:8000/health` | FastAPI REST API serving detection engines & policy rules |
| **Frontend UI** | `http://localhost:3000` / `http://localhost:80` | `http://localhost:80/nginx-health` | React Single-Page Application (Customer Checkout, Risk Ops Console, Attack Simulator) |

---

## 4. Stopping Container Services

```bash
docker compose down
```
To remove persistent volumes as well:
```bash
docker compose down -v
```
