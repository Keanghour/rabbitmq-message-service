from pydantic import BaseModel
from typing import List, Dict

class QueueMessageRequest(BaseModel):
    trxnRef: str
    queueName: str
    data: List[Dict]