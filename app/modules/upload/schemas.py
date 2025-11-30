from pydantic import BaseModel

class PresignRequest(BaseModel):
    content_type: str
    extension: str

