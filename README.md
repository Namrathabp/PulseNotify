# PulseNotify Backend

PulseNotify is an automated, asynchronous flight price monitoring and alerting engine. Users can create custom price thresholds for targeted airline routes, and a distributed background worker network continuously queries simulated price feeds, dispatching data-logged notifications the instant a price target is met.

This system demonstrates asynchronous processing with **Celery**, background task orchestration with **Celery Beat**, containerized dependency isolation using **Podman**, and modular enterprise configurations in **Django**.

---

## Technical Stack & Infrastructure
* **Host Environment:** Windows Subsystem for Linux (WSL2 - Ubuntu)
* **Application Framework:** Django 5.0 / Django REST Framework 3.15
* **Authentication Engine:** SimpleJWT (JSON Web Tokens)
* **Container Core Engine:** Podman (Rootless Docker Alternative)
* **Database Management:** PostgreSQL 15 (Containerized)
* **Message Broker:** Redis 7 (Containerized)
* **Task Queues:** Celery 5.4 & Celery Beat Scheduler

---

## How to run this project

## 1. Local Infrastructure Configuration (Podman)

Because Podman runs securely in rootless mode, run the following commands in your WSL terminal to pull official registry references and spin up persistent database and caching instances:

```bash
# Create a dedicated local data persistence volume for PostgreSQL
podman volume create postgres_data

# Launch containerized PostgreSQL with standard system profiles
podman run -d --name pulsenotify_db \
  -e POSTGRES_DB=pulsenotify_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data:Z \
  docker.io/library/postgres:15-alpine

# Launch containerized Redis Cache to handle Celery task transactions
podman run -d --name pulsenotify_redis \
  -p 6379:6379 \
  docker.io/library/redis:7-alpine
```
## 2. To verify the container is running
```
podman ps
```
## 3. Initialize local python environment
```
# 1. Update package managers and verify system tools exist
sudo apt update
sudo apt install python3-pip python3-venv libpq-dev build-essential -y

# 2. Build and enter an isolated virtual environment shell
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade your package delivery core and pull project components
pip install --upgrade pip
pip install -r requirements.txt

```

## 4. Configuration and Database Synchronization
```
# Inform Django to route execution context to our split local configuration file
export DJANGO_SETTINGS_MODULE=pulse_project.settings.local

# Run standard structural database migrations to populate PostgreSQL tables
python manage.py makemigrations pulse
python manage.py migrate
```

## 5. Run Execution playbook (3 Terminals)
## Terminal 1: Django core web Gateway
```
python manage.py runserver
```
## Terminal 2: Celery Background job worker
```
celery -A pulse_project worker --loglevel=info
```
## Terminal 3: Celery beat periodic clock scheduler
```
celery -A pulse_project beat --loglevel=info
```

## 6. Automated verification and testing
```
python manage.py test
```
## API Reference & Postman Test Verification Matrix
1	Register a new user	POST /api/auth/register/	201 Created	Public
<img width="940" height="706" alt="image" src="https://github.com/user-attachments/assets/81528062-7db6-4b22-b2e9-9f8a20e33ef1" />

2	Register duplicate username	POST /api/auth/register/	400 Bad Request	Public
<img width="940" height="433" alt="image" src="https://github.com/user-attachments/assets/e1656301-4149-4090-91c2-fc2f62f26f63" />

3	Create a price alert - no token	POST /api/alerts/	401 Unauthorized	Public
<img width="940" height="405" alt="image" src="https://github.com/user-attachments/assets/848f4b64-c469-464d-853e-560b940cb9fd" />

4	Create a price alert - valid token	POST /api/alerts/	201 Created	Valid Bearer Token
<img width="940" height="706" alt="image" src="https://github.com/user-attachments/assets/ab9c56ea-c68d-4436-8b93-219e55a48c5d" />

5	List logged-in user's alerts	GET /api/alerts/	200 OK + Array	Valid Bearer Token
<img width="940" height="482" alt="image" src="https://github.com/user-attachments/assets/1ab9f106-f572-4ab7-87b0-3df35640fd1f" />

6	Deactivate an active alert	DELETE /api/alerts/<id>/	200 OK + Inactive	Valid Bearer 
<img width="940" height="424" alt="image" src="https://github.com/user-attachments/assets/6baf5c73-116e-4506-bacf-7d3afca576ac" />

7	Mock price feed - valid route	GET /api/flights/price/?route=DEL-BOM	200 OK + Price	Public
<img width="940" height="469" alt="image" src="https://github.com/user-attachments/assets/9916c7e1-b9ad-4cbc-b57b-24e020c49d18" />

8	Mock price feed - invalid route	GET /api/flights/price/?route=XYZ-ABC	404 Not Found	Public
<img width="940" height="442" alt="image" src="https://github.com/user-attachments/assets/0ecbfc3e-df86-4932-8a16-46981869486d" />

9	Admin summary - user token	GET /api/admin/summary/	403 Forbidden	Valid Bearer Token
<img width="940" height="459" alt="image" src="https://github.com/user-attachments/assets/757f69b6-04f6-47b1-8cf9-0dfa0ff19bd9" />





