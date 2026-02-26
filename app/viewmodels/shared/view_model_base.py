from starlette.requests import Request
from starlette.responses import Response
from typing import Optional


class ViewModelBase:
    def __init__(self, request: Request, response: Optional[Response] = None):
        self.request: Request = request
        self.response: Optional[Response] = response
        self.error: Optional[str] = None

    def to_dict(self) -> dict:
        return self.__dict__
