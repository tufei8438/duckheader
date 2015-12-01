#coding:utf8

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
import jinja2
from tornado.web import RequestHandler


class BaseRequestHandler(RequestHandler):

    __path_to_env = dict()

    def create_template_loader(self, template_path):
        temp_path = template_path
        if isinstance(template_path, (list, tuple)):
            temp_path = template_path[0]

        env = BaseRequestHandler.__path_to_env.get(temp_path)
        if not env:
            _loader = jinja2.FileSystemLoader(template_path)
            env = jinja2.Environment(loader=_loader)
            BaseRequestHandler.__path_to_env[temp_path] = env
        return env

    def render_string(self, template_name, **kwargs):
        env = self.create_template_loader(self.get_template_path())
        t = env.get_template(template_name)
        namespace = self.get_template_namespace()
        namespace.update(kwargs)
        return t.render(**namespace)

    def data_received(self, chunk):
        pass
