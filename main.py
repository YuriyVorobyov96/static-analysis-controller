from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from pathlib import Path
import re
import socketserver
import sys

load_dotenv()

sys.path.append('./src/app')
sys.path.append('./src/scanner')
sys.path.append('./src/www')

from http_utils import HTTPUtils
from app_controller import AppController
from issues_controller import IssuesController
from project_controller import ProjectController
from scan_controller import ScanController
from token_controller import TokenController

class App(BaseHTTPRequestHandler):
    @classmethod
    def use_documentation(cls, doc_dir, doc_driver_dir):
      cls.doc_dir = Path(__file__).resolve().parent / doc_dir
      cls.doc_driver_dir = Path(__file__).resolve().parent / doc_driver_dir

    @classmethod
    def use_static(cls, static_dir):
      cls.static_dir = Path(__file__).resolve().parent / static_dir

    @classmethod
    def use_http(cls):
      cls.http = HTTPUtils()

    @classmethod
    def use_controllers(cls, app_controller, issues_controller, project_controller, scan_controller, token_controller):
      cls.app_controller = app_controller()
      cls.issues_controller = issues_controller()
      cls.project_controller = project_controller()
      cls.scan_controller = scan_controller()
      cls.token_controller = token_controller()

    def do_GET(self):
        path = self.http.get_path_url(self)

        if path == '/help':
          return self.app_controller.help_message(self)

        if path == '/scanner/project/search':
          return self.project_controller.search_project(self)

        if path == '/scanner/issues/search':
          return self.issues_controller.get_issues(self)
        
        if path == '/scanner/issues/get-all-security-issues':
          return self.issues_controller.get_all_security_issues(self)

        if path == '/scanner/scan/report':
          return self.scan_controller.scan_report(self, self.static_dir)

        if path == '/docs/raw':
          return self.app_controller.get_docs_raw(self, self.doc_dir)

        if path == '/docs/openapi':
          return self.app_controller.get_openapi_documentation(self, self.doc_dir)

        if re.match(r"/docs/", path):
          if self.path[5:] == '/openapi.yaml':
            return self.app_controller.get_openapi_file(self, self.doc_dir, file_name=self.path[6:])
          else:
            return self.app_controller.serve_static(self, self.doc_driver_dir, file_name=self.path[6:])

        return self.http.send_not_found_error(self)

    def do_POST(self):
      path = self.http.get_path_url(self)

      if path == '/scanner/project/create':
        return self.project_controller.create_project(self)

      if path == '/scanner/token/create':
        return self.token_controller.create_analysis_token(self)

      if path == '/scanner/scan/init':
        return self.scan_controller.init_scan(self)

      if path == '/scanner/scan/analysis':
        return self.scan_controller.full_analysis(self)

      return self.http.send_not_found_error(self)


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, host='0.0.0.0', port=8000):
    print(f'Server started at port {port}. Press CTRL+C to close the server.')

    server_address = (host, port)

    handler_class.use_http()
    handler_class.use_controllers(
      app_controller = AppController,
      issues_controller = IssuesController,
      project_controller = ProjectController,
      scan_controller = ScanController,
      token_controller = TokenController
    )
    handler_class.use_documentation(
      doc_dir = 'documentation',
      doc_driver_dir = 'documentation/swagger'
    )
    handler_class.use_static(
      static_dir = 'static',
    )

    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server Closed')

run(socketserver.TCPServer, App)
