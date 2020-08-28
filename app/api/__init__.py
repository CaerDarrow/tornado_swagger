from tornado.web import url
from .test.handler import TestHandler
from ._docs.handler import SwaggerHomeHandler

API_VERSION = 'v0.1'

api_routes = [
    # docs
    url(fr'/api/{API_VERSION}/docs', SwaggerHomeHandler),

    # test
    url(fr'/api/{API_VERSION}/test/([a-zA-Z0-9\-]+)', TestHandler),

]
