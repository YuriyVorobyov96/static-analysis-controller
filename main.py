from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
import re
from ruamel.yaml import YAML
import socketserver
import sys

load_dotenv()

sys.path.append('./src/www')
sys.path.append('./src/scanner')

from http_utils import HTTPUtils
from issues_controller import IssuesController
from project_controller import ProjectController
from scan_controller import ScanController
from token_controller import TokenController

yaml = YAML(typ='safe')

class App(BaseHTTPRequestHandler):
    @classmethod
    def use_documentation(cls, doc_dir, doc_driver_dir):
      cls.doc_dir = Path(__file__).resolve().parent / doc_dir
      cls.doc_driver_dir = Path(__file__).resolve().parent / doc_driver_dir

    @classmethod
    def use_http(cls):
      cls.http = HTTPUtils()

    @classmethod
    def use_controllers(cls, issues_controller, project_controller, scan_controller, token_controller):
      cls.issues_controller = issues_controller()
      cls.project_controller = project_controller()
      cls.scan_controller = scan_controller()
      cls.token_controller = token_controller()

    def do_GET(self):
        path = self.http.get_path_url(self)

        if path == '/help':
          return self.__help_message()

        if path == '/scanner/project/search':
          return self.project_controller.search_project(self)

        if path == '/scanner/issues/search':
          return self.issues_controller.get_issues(self)

        if path == '/docs/raw':
          return self.__get_docs_raw()

        if path == '/docs/openapi':
          try:
              self.path = self.doc_dir / 'index.html'
              with open(self.path, 'rb') as file:
                self.http.send_response(self, 200)
                self.http.send_header(self, 'Content-type', 'text/html')
                self.http.end_headers(self)
                return self.http.serve_file(self, file)
          except FileNotFoundError:
            return self.http.send_bad_request_error(self, 'Documentation not found')

        if re.match(r"/docs/", path):
          if self.path[5:] == '/openapi.yaml':
            with open(os.path.join(self.doc_dir, self.path[6:]), 'rb') as file:
              self.http.send_response(self, 200)
              self.http.send_header(self, 'Content-type', 'text/plain')
              self.http.end_headers(self)
              return self.http.serve_file(self, file)
          else:
            with open(os.path.join(self.doc_driver_dir, self.path[6:]), 'rb') as file:
              self.http.send_response(self, 200)
              if self.path.endswith('.html'):
                self.http.send_header(self, 'Content-type', 'text/html')
              if self.path.endswith('.css'):
                self.http.send_header(self, 'Content-type', 'text/css')
              if self.path.endswith('.css'):
                self.http.send_header(self, 'Content-type', 'text/png')
              elif self.path.endswith('.js'):
                self.http.send_header(self, 'Content-type', 'application/javascript')
              self.http.end_headers(self)
              return self.http.serve_file(self, file)

        return self.http.send_not_found_error(self)

    def do_POST(self):
      path = self.http.get_path_url(self)

      if path == '/scanner/project/create':
        return self.project_controller.create_project(self)

      if path == '/scanner/token/create':
        return self.token_controller.create_analysis_token(self)

      if path == '/scanner/scan/init':
        return self.scan_controller.init_scan(self)

      return self.http.send_not_found_error(self)

    def __help_message(self):
      message = ('Welcome to Analysis Controller\n'
        'To perform actions send requests to specified routes\n'
        '\n'
        'Documentation available via GET /docs/openapi'
        '}\n')

      self.send_result(200, message)

    def __get_docs_raw(self):
      try:
        with open('./openapi.yaml') as f:
          self.http.send_result(self, 200, json.dumps(yaml.load(f)))
      except Exception as err:
        print('Documentation parse error: ', err)
        self.http.send_bad_request_error(self, 'Exception while load openapi documentation')


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, host='0.0.0.0', port=8000):
    print(f'Server started at port {port}. Press CTRL+C to close the server.')

    server_address = (host, port)

    handler_class.use_http()
    handler_class.use_controllers(
      issues_controller = IssuesController,
      project_controller = ProjectController,
      scan_controller = ScanController,
      token_controller = TokenController
    )
    handler_class.use_documentation(
      doc_dir = 'documentation',
      doc_driver_dir = 'documentation/swagger'
    )

    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server Closed')

run(socketserver.TCPServer, App)
