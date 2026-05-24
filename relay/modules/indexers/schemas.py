from pydantic import BaseModel


class LoginIndexer(BaseModel):
    indexer_id: str
    username: str
    password: str
