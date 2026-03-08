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