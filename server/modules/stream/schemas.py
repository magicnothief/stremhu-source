from pydantic import BaseModel


class ParsedRangeHeader(BaseModel):
    start_byte: int
    end_byte: int
    content_length: int
