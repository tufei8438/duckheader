# coding:utf8

"""
Copyright 2015 tufei

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import tornado.ioloop
import tornado.httpserver
import venusian
import duckheader.handlers
from tornado.web import Application


class DuckheaderApplication(Application):

    HANDLERS = []

    def route(self, pattern, kwargs=None, name=None):
        def decorator(cls):
            self.add_handler(pattern, cls, kwargs, name)
            return cls
        return decorator

    def add_handler(self, pattern, cls, kwargs=None, name=None):
        self.HANDLERS.append((pattern, cls, kwargs, name))

    def finish_route(self):
        self.add_handlers(".*$", self.HANDLERS)

app_path = os.getcwd()

settings = {
    'debug': True,
    'static_path': os.path.join(app_path, 'static'),
    'template_path': os.path.join(app_path, 'templates')
}

app = DuckheaderApplication(**settings)


def http_serve(port=8348):
    ioloop = tornado.ioloop.IOLoop.instance()

    scanner = venusian.Scanner()
    scanner.scan(duckheader.handlers, ignore=None)
    app.finish_route()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)

    ioloop.start()