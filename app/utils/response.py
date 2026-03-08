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

def error(trxnRef: str = None, queueName: str = None, error: str = None, desc: str = "Queue processing failed"):
    return api_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        desc=desc,
        trxnRef=trxnRef,
        queueName=queueName,
        messageCount=0,
        error=error
    )