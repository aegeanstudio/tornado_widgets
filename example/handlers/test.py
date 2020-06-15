# -*- coding: UTF-8 -*-

from marshmallow import Schema, fields, EXCLUDE

from example.handlers import router, spec
from tornado_widgets.handler import JSONHandler
from tornado_widgets.schema import schema


class RequestTestAPIQueryArgs(Schema):
    name = fields.String(required=True, description='名字')


class RequestTestAPIJSONBody(Schema):
    test = fields.String(required=True, description='测试字段')


class ResponseTestAPI(Schema):
    name = fields.String(description='名字')
    test = fields.String(description='测试字段')


@router.route(route='/test')
class TestHandler(JSONHandler):

    @schema(query_args=RequestTestAPIQueryArgs(unknown=EXCLUDE),
            json_body=RequestTestAPIJSONBody(), res=ResponseTestAPI(),
            reg_to=spec)
    async def post(self):
        """---
        description:
          测试JSON返回
        parameters:
          - in: query
            schema: RequestTestAPIQueryArgs
        requestBody:
          content:
            application/json:
              schema: RequestTestAPIJSONBody
        responses:
          200:
            content:
              application/json:
                schema: ResponseTestAPI"""
        return dict(**self.query_args, **self.json_body)
