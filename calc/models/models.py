from pydantic import BaseModel


# features
# 1. It's just plain python
# 2. Built in async
# 3. Built in data validation using pydantic
# 4. Typed python
# 5. Errors in json
# 6. Authentication built in
# 7. Swagger and ReDoc built-in


class SignalReq(BaseModel):
    ltp: str
    scrip: str


class SignalResp(BaseModel):
    signal: str


class Signal(BaseModel):
    scrip: str
    low: float
    high: float
