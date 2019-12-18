# -*- coding: UTF-8 -*-

import asyncio

from tornado.options import define

from tornado_widgets.app import App
from tornado_widgets.handler import JSONHandler


define('debug', True)
define('port', 8080)


app = App(name='example')
app.run


@app.route('/api/v1/test')
class TestHandler(JSONHandler):

    async def get(self):
        print(dict(self.request.headers.get_all()))
        await asyncio.sleep(1)
        self.write('{"Hello": "World!"}\n')


if __name__ == '__main__':
    app.run()
