import typing
from tornado import web
from inspect import signature

import collections
import inspect
import os
import re
import typing
import pydantic
import json

import tornado.web

swagger_models = {}

# def _save_model_doc(model):
#     global swagger_models
#     doc = model.__doc__
#
#     if doc is not None and '---' in doc:
#         swagger_models[model.__name__] = extract_swagger_docs(doc)


# def register_swagger_model(model):
#     _save_model_doc(model)
#     return model

def _build_method_docs(method_handler):
    swagger_obj = {"produces": ["application/json"], "tags": ["Example"]}
    # META-информация

    doc = inspect.unwrap(method_handler).__doc__
    endpoint_doc = doc.splitlines()

    for line in endpoint_doc:
        line = line.strip()
        if line:
            k, v = line.split(':')
            swagger_obj[k.strip()] = v.strip()
    sig = signature(method_handler)
    print(method_handler.body)
    # for param in sig.parameters:
    #     print(param)
    # АРГУМЕНТЫ PATH
    swagger_obj["parameters"] = [
       {
           "in": "path",
           "name": "user_id",
           "type": "string",
       },
    ]
    # АРГУМЕНТЫ QUERY
    for query_arg in method_handler.query:
        swagger_obj["parameters"].append(
            {
                "in": "query",
                "name": query_arg,
                "type": "string",
            }
        )
    # BODY
    if method_handler.body:
        swagger_obj["parameters"].append(
            {
                "in": "body",
                "schema": method_handler.body.schema(),
            }
        )
    # RESPONSES
    swagger_obj["responses"] = {}
    for response in method_handler.responses:
        response_dict = {"description": response.reason}
        print()
        try:
            response_dict.update({"schema": response.data.schema()})
        except AttributeError:
            pass
        swagger_obj["responses"].update({
            response.status_code: response_dict
        })
        # print(json.dumps(sig.return_annotation.schema(), indent=4))
    return swagger_obj


def _build_path_doc(handler):
    docs = {}
    for method in handler.SUPPORTED_METHODS:
        method = method.lower()
        method_handler = getattr(handler, method)  # attribute error
        docs.update({
            method: _build_method_docs(method_handler=method_handler)
        })
    return docs


def _build_endpoint_docs(swagger, route):
    if route.target.SWAGGED:
        formated_path = _format_handler_path(route)
        path_doc = _build_path_doc(handler=route.target)
        swagger['paths'][formated_path.replace(swagger['basePath'], '')].update(path_doc)


def generate_doc_from_endpoints(routes: typing.List[tornado.web.URLSpec],
                                *,
                                api_version):

    # The Swagger OBJ
    swagger = {
        'swagger': '2.0', 'info': {
            'description': 'Первая версия API',
            'version': api_version,
            'title': 'Тетрика API',
            'contact': {
                'name': 'Иван Сизов'
            }
        }, 'basePath': f'/api/{api_version}', 'paths': collections.defaultdict(dict), 'definitions': swagger_models}
    # if security_definitions:
    #     swagger['securityDefinitions'] = nesteddict2yaml(security_definitions)

    # swagger['schemes'] = schemes

    for route in routes:
        _build_endpoint_docs(swagger=swagger, route=route)

    return swagger


def _format_handler_path(route):
    brackets_regex = re.compile(r'\(.*?\)')
    parameters = _extract_parameters_names(route.target, route.regex.groups)
    route_pattern = route.regex.pattern

    for i, entity in enumerate(brackets_regex.findall(route_pattern)):
        route_pattern = route_pattern.replace(entity, f"{{{parameters[i]}}}", 1)

    return route_pattern[:-1]


def _extract_parameters_names(handler, parameters_count):
    if parameters_count == 0:
        return []

    parameters = ['{?}' for _ in range(parameters_count)]

    for method in handler.SUPPORTED_METHODS:
        method_handler = getattr(handler, method.lower())
        args = _try_extract_args(method_handler)

        if len(args) > 0:
            for i, arg in enumerate(args):
                if set(arg) != {'_'} and i < len(parameters):
                    parameters[i] = arg

    return parameters


def _try_extract_args(method_handler):
    return inspect.getfullargspec(inspect.unwrap(method_handler)).args[1:]


def setup_swagger2(routes: typing.List[tornado.web.URLSpec],
                  *,
                  api_version,
                  security_definitions: dict = None
                  ):
    swagger = generate_doc_from_endpoints(routes, api_version=api_version)

    swagger["paths"] = {
            "/api/test/{user_id}": {
                "get": {
                    "tags": [
                        "Example"
                    ],
                    "summary": "Create user",
                    "description": "This can only be done by the logged in user.",
                    "operationId": "examples.api.api.createUser",
                    "produces": [
                        "application/json"
                    ],
                    "parameters": [
                        {
                            "in": "request",
                            "name": "user_id",
                            "type": "integer",
                        },
                        # {
                        #     "in": "body",
                        #     "name": "body",
                        #     "description": "Created user object",
                        #     "required": False,
                        #     "schema": {
                        #     }
                        # }
                    ],
                    "responses": {
                        "200": {
                            "description": "successful operation",
                            "schema": {
                                'title': 'UserModel',
                                'type': 'object',
                                'properties': {'name': {'title': 'Name', 'type': 'string'},
                                               'username': {'title': 'Username', 'type': 'string'},
                                               'password1': {'title': 'Password1', 'type': 'string'},
                                               'password2': {'title': 'Password2', 'type': 'string'},
                                               'date': {'title': 'Date', 'default': '2020-08-25T01:14:35.347843',
                                                        'type': 'string', 'format': 'date-time'}},
                                'required': ['name', 'username', 'password1', 'password2']}

                        }
                    }
                }
            }
        }
    return swagger
