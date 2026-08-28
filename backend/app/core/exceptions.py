class CEAException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResearchNotFoundError(CEAException):
    def __init__(self, research_id: str):
        super().__init__(f"Research '{research_id}' not found", 404)


class LLMProviderError(CEAException):
    def __init__(self, message: str):
        super().__init__(message, 503)
