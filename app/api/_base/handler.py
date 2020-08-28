from typing import Type, Optional
from functools import wraps
from tornado import web, escape
from pydantic import BaseModel
from .model import BaseResponse


class Swagger(object):

    def __init__(self, body=None, query=(), responses=()):
        self._body = body
        self._query = query
        self._responses = responses

    def __call__(self, function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            result = await function(*args, **kwargs)
            return result

        # some magic here (we wantn't change func signature)
        wrapper.body = self._body
        wrapper.query = self._query
        wrapper.responses = self._responses
        return wrapper


class BaseHandler(web.RequestHandler):
    def _read_body(self):
        body = self.request.body
        if not body:
            raise Exception('empty body')

        decoded_body = escape.json_decode(body)
        return decoded_body

    def get_body(self, model: Type[BaseModel]):
        body = self._read_body()
        return model.parse_obj(body)

    def get_trusted_body(self, model: Type[BaseModel]):
        """
            No validation!
        """
        body = self._read_body()
        return model.construct(**body)

    OK_RESPONSE = BaseResponse(status_code=200, reason='OK')

    def finish_with_ok(self, response: BaseResponse = OK_RESPONSE):
        assert response.status_code in range(200, 207)
        self.set_status(response.status_code, response.reason)
        if response.data:
            self.write(response.data.json())
        return self.finish()

    ERROR_RESPONSE = BaseResponse(status_code=400, reason='ERROR')

    def finish_with_error(self, response: BaseResponse = ERROR_RESPONSE):
        assert response.status_code in range(400, 452)
        self.set_status(response.status_code, response.reason)
        if response.data:
            self.write(response.data.json())
        return self.finish()

