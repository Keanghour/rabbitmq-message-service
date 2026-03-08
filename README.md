# FastAPI service for publishing JSON messages to RabbitMQ queues with dynamic queue creation and clean API responses.

**Created by: Hour Zackry**

# **RabbitMQ + FastAPI Project Developer Guide**

## **Project Overview**

This project is a **FastAPI service** that accepts JSON payloads and publishes messages to RabbitMQ queues.

* Supports dynamic queues.
* RabbitMQ vhost and user follow the environment variables.
* Provides a clean JSON API response format.

---

## **Folder Structure**

```text
project-root/
├─ app/
│  ├─ main.py
│  ├─ models.py
│  ├─ rabbitmq.py
│  ├─ utils/
│  │  └─ response.py
│  ├─ routes/
│  │  └─ queue_routes.py
│  └─ middleware/
│     └─ custom_exceptions.py
├─ .env
├─ requirements.txt
└─ README.md
```

---

## **1️⃣ Environment Variables**

Create `.env` in the project root:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=keanghour
RABBITMQ_PASSWORD=Hour@1234
RABBITMQ_VHOST=/keanghour
```

> These values are used by FastAPI to connect to RabbitMQ.

---

## **2️⃣ Docker Setup for RabbitMQ**

Run RabbitMQ container **with custom user and vhost**:

```bash
docker run -d --hostname my-rabbit --name rabbitmq \
  -p 0000:0000 -p 00000:00000 \
  -e RABBITMQ_DEFAULT_USER=xxxx \
  -e RABBITMQ_DEFAULT_PASS=xxxx \
  -e RABBITMQ_DEFAULT_VHOST=/ \
  rabbitmq:3-management
```

* **Ports:**

  * `5672` → AMQP
  * `15672` → Management UI

* **Management UI:** [http://localhost:00000](http://localhost:00000)

  * Username: `xxxx`
  * Password: `xxxx`
  * Vhost: `/`

> Optional: If you already have RabbitMQ running, remove old containers first:

```bash
docker rm -f rabbitmq
```

---

## **3️⃣ Python Dependencies**

Create `requirements.txt`:

```text
fastapi
uvicorn
pika
python-dotenv
pydantic
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## **4️⃣ FastAPI Code**

### **4a. app/main.py**

```python
from fastapi import FastAPI
from app.routes.queue_routes import router

app = FastAPI()
app.include_router(router)
```

---

### **4b. app/models.py**

```python
from pydantic import BaseModel
from typing import List, Dict

class QueueMessageRequest(BaseModel):
    trxnRef: str
    queueName: str
    data: List[Dict]
```

---

### **4c. app/middleware/custom_exceptions.py**

```python
class QueueError(Exception):
    pass
```

---

### **4d. app/utils/response.py**

```python
from datetime import datetime
from fastapi import status

def api_response(status_code: int, desc: str, **kwargs):
    response = {
        "code": str(status_code),
        "desc": desc,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    response.update(kwargs)
    return response

def success(trxnRef: str, queueName: str, messageCount: int = 1, desc: str = "Message queued successfully"):
    return api_response(
        status_code=status.HTTP_200_OK,
        desc=desc,
        trxnRef=trxnRef,
        queueName=queueName,
        messageCount=messageCount
    )

def error(trxnRef: str = None, queueName: str = None, error_message: str = None, desc: str = "Queue processing failed"):
    return api_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        desc=desc,
        trxnRef=trxnRef,
        queueName=queueName,
        error=error_message
    )
```

---

### **4e. app/rabbitmq.py**

```python
import os
import pika
import json
from app.middleware.custom_exceptions import QueueError

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    try:
        return pika.BlockingConnection(parameters)
    except Exception as e:
        raise QueueError(f"Cannot connect to RabbitMQ: {str(e)}")

def publish(queue_name: str, messages: list):
    if not queue_name:
        raise QueueError("Queue name cannot be empty")

    try:
        connection = get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        for msg in messages:
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(msg),
                properties=pika.BasicProperties(delivery_mode=2)
            )

        connection.close()
    except QueueError:
        raise
    except Exception as e:
        raise QueueError(f"Failed to publish message: {str(e)}")
```

---

### **4f. app/routes/queue_routes.py**

```python
from fastapi import APIRouter
from app.models import QueueMessageRequest
from app.utils.response import api_response
from app.rabbitmq import publish
from app.middleware.custom_exceptions import QueueError

router = APIRouter()

@router.post("/queue-messages")
def queue_messages(req: QueueMessageRequest):
    try:
        publish(req.queueName, req.data)
        return api_response(
            status_code=200,
            desc="Message queued successfully",
            trxnRef=req.trxnRef,
            queueName=req.queueName,
            messageCount=len(req.data)
        )
    except QueueError as e:
        return api_response(
            status_code=500,
            desc="Queue processing failed",
            trxnRef=req.trxnRef,
            queueName=req.queueName,
            error=str(e)
        )
```

---

## **5️⃣ Running FastAPI**

```bash
uvicorn app.main:app --reload
```

* FastAPI will run on [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## **6️⃣ Testing with Postman**

POST: `http://127.0.0.1:8000/queue-messages`

**Request Body:**

```json
{
  "trxnRef": "TX1001",
  "queueName": "test_queue",
  "data": [{"orderId": "ORD001", "amount": 200}]
}
```

**Response (success):**

```json
{
  "code": "200",
  "desc": "Message queued successfully",
  "trxnRef": "TX1001",
  "queueName": "test_queue",
  "messageCount": 1,
  "timestamp": "2026-03-08T09:30:00Z"
}
```

**Response (queue missing or error):**

```json
{
  "code": "500",
  "desc": "Queue processing failed",
  "trxnRef": "TX1001",
  "queueName": "test_queue",
  "error": "Cannot connect to RabbitMQ: NOT_ALLOWED - vhost / not found",
  "timestamp": "2026-03-08T09:31:00Z"
}
```
<img width="2118" height="944" alt="image" src="https://github.com/user-attachments/assets/36d1c3c0-95d3-42e4-adfc-eb5ada3e63fb" />
<img width="2876" height="1634" alt="image" src="https://github.com/user-attachments/assets/0436f6dd-9337-48b4-857e-602232e70992" />

---

## **7️⃣ Management UI**

* URL: [http://localhost:00000](http://localhost:00000)
* User: `xxxx`
* Password: `xxxx`
* Vhost: `/`

---

## **8️⃣ Notes**

* FastAPI **does not create RabbitMQ users or vhosts**; Docker environment variables handle this automatically.
* If you already have RabbitMQ, make sure vhost `/` exists and user has permissions:

```bash
docker exec -it rabbitmq bash
rabbitmqctl add_vhost /
rabbitmqctl add_user xxxx xxxx
rabbitmqctl set_permissions -p / xxxx ".*" ".*" ".*"
```

* **Queues** are created dynamically by the API (`channel.queue_declare`) if they don’t exist.

## ☕ Support / Buy Me a Coffee

If you like this project and want to support me, you can:

| Option            | Link / QR                                            |
| ----------------- | ---------------------------------------------------- |
| 🏦 **ABA Bank QR** | [ABA Bank QR](https://pay.ababank.com/oRF8/fe6dcb9h) |
| 💬 **Telegram**   | [@phokeanghour](https://t.me/phokeanghour)           |

> 🙏 Your support helps me keep building and improving this project!
