from http import HTTPStatus
from string import Template

from fastapi import HTTPException


class APIException(HTTPException):
    message = str()
    code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, **kwargs):
        self.message = Template(self.message).substitute(**kwargs)
        super().__init__(status_code=self.code.real, detail=self.message)
