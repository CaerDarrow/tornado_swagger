# external packages
import asyncio
import os
import signal
import uvloop
from functools import partial
from tornado import (
    ioloop, locks, web, options
)

# internal packages
from api import api_routes, API_VERSION
from build_api_docs import generate_doc_from_endpoints


class Application(web.Application):
    def __init__(self, routes, pg_pool):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
        )
        self.SWAGGER_SCHEMA = generate_doc_from_endpoints(routes, api_version=API_VERSION)
        super(Application, self).__init__(routes, **settings)


shutdown_event = locks.Event()


async def on_shutdown(app):
    #  cleanup_context
    shutdown_event.set()


def exit_handler(app, sig, frame):
    ioloop.IOLoop.instance().add_callback_from_signal(on_shutdown, app)


async def main():
    routes = api_routes
    app = Application(routes=routes, pg_pool=None)
    # ioloop.IOLoop.current().spawn_callback(listen_to_redis, app)
    app.listen(port=80)
    # tornado_api_doc(app, config_path='./conf/test.yaml', url_prefix='/api/doc', title='API doc')
    signal.signal(signal.SIGTERM, partial(exit_handler, app))
    signal.signal(signal.SIGINT, partial(exit_handler, app))
    await shutdown_event.wait()


if __name__ == "__main__":
    options.parse_command_line()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    ioloop.IOLoop.current().run_sync(main)
