# -*- coding: UTF-8 -*-

from tornado_widgets.app import App

from example import config
from example.handlers import router, spec

app = App(name='example', config=config)

app.register_router(route_obj=router)
app.register_spec(spec_obj=spec)


if __name__ == '__main__':
    app.run()
