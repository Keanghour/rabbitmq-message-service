class QueueError(Exception):
    """
    Raised when there is a queue/publishing error
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """
    Custom validation error for bad requests
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)