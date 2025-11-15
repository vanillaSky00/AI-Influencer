# Vanilla Meow — AI Cat Avatar 🐱

<br>
<p align="center">
  <img src="assets/screenshots/gui-mac.png" width="650">
</p>

A small but complete demo of an AI-driven “cat influencer” that chats and posts, powered by OpenAI, FastAPI, Celery, and a lightweight GUI built for macOS.

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-109989?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" />
  <img src="https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <br />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Uvicorn-64D2FF?style=for-the-badge&logo=uvicorn&logoColor=black" />
  <br />
  <img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white" />
  <img src="https://img.shields.io/badge/XQuartz-FF6600?style=for-the-badge&logo=x.org&logoColor=white" />
  <img src="https://img.shields.io/badge/socat-50A14F?style=for-the-badge" />
</p>




## 🌱 Setting Up the Environment
### Step 1. Clone repo & create .env
```
cd backend
cp .env.example .env
```
Example .env:
```
OPENAI_API_KEY=sk-...
RABBITMQ_USER=user
RABBITMQ_PASS=password
CELERY_BROKER_URL=amqp://user:password@rabbitmq:5672//
CELERY_BACKEND_URL=redis://redis:6379/0
TIMEZONE=Asia/Taipei
```
### Step 2. Run the Mac startup script
```
./run.sh
```
This script:
- Ensures `Docker Desktop` is running
- Launches `XQuartz` and grants `X11 access`
- Starts a socat bridge (TCP 6000 → UNIX socket)
- Runs `docker compose` --profile mac up --build
- You’ll see a window titled Vanilla Meow 🐱
3. Open browser for backend docs
```
http://localhost:8000/docs
```
You can test endpoints like /api/avatar/reply or /api/tasks/{id} here.

## 🌐 Overview
Vanilla Meow is an AI Cat Avatar that lives in a containerized environment and responds to user prompts like a playful digital pet.
It demonstrates:
- `FastAPI` serving as the REST API backend
- `Celery` background tasks processing AI replies asynchronously
- `RabbitMQ` + `Redis` for message queue and result backend
- `OpenAI API` structured outputs (gpt-4o-mini)
- Frontend (chat-mac) rendered through `XQuartz` on macOS

## 🧱 Architecture
```
frontend (chat-mac GUI) ─▶ web (FastAPI)
                                  │
                                  ▼
                        celery_worker (background tasks)
                          ├── RabbitMQ → message broker
                          └── Redis → result backend
```

Service
| Service           | Role                             | Ports                    |
| ----------------- | -------------------------------- | ------------------------ |
| **web**           | FastAPI API Server               | 8000                     |
| **celery_worker** | Executes AI tasks asynchronously | –                        |
| **rabbitmq**      | Message broker                   | 15672 (UI) / 5672 (AMQP) |
| **redis**         | Task result backend              | 6379                     |
| **chat-mac**      | GUI client (X11 via XQuartz)     | –                        |

## 🎒 Requirements
- macOS 13 or later
- Docker Desktop (latest)
- Homebrew with socat and XQuartz
- OpenAI API key (Pay-As-You-Go, not ChatGPT Plus)

