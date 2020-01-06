# -*- coding: UTF-8 -*-

from marshmallow import Schema, fields

from tornado_widgets.handler import JSONHandler

from example.handlers import router, spec
from tornado_widgets.schema import schema


class RequestTestAPI(Schema):
    name = fields.String(required=True, description='名字')


class ResponseTestAPI(Schema):
    name = fields.String(required=True, description='名字')


@router.route(route='/test')
class TestHandler(JSONHandler):

    @schema(query_args=RequestTestAPI, res=ResponseTestAPI, reg_to=spec)
    async def get(self):
        """---
        description:
          测试JSON返回
        parameters:
          - in: query
            schema: RequestTestAPI
        responses:
          200:
            content:
              application/json:
                schema: ResponseTestAPI"""
        return self.query_args
