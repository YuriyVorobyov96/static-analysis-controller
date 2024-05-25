from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
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

class App(BaseHTTPRequestHandler):
    @classmethod
    def use_http(cls):
      cls.http = HTTPUtils()

    @classmethod
    def use_controllers(cls):
      cls.issues_controller = IssuesController()
      cls.project_controller = ProjectController()
      cls.scan_controller = ScanController()
      cls.token_controller = TokenController()

    def do_GET(self):
        path = self.http.get_path_url(self)

        if path == '/help':
          return self.__help_message()

        if path == '/scanner/project/search':
          return self.project_controller.search_project(self)

        if path == '/scanner/issues/search':
          return self.issues_controller.get_issues(self)

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
        message = ('Welcome to static analysis controller\n'
            'To perform action send request with GET\n'
            '\n'
            'Body fields:\n'
            'target - target to sending HTTP request - REQUIRED\n'
            'method - HTTP request method (GET|POST|PUT|PATCH|DELETE) - REQUIRED\n'
            'headers - HTTP request headers - OPTIONAL\n'
            'payload - body for HTTP request - OPTIONAL\n'
            'param - param for update to random value for HTTP request modification - OPTIONAL\n'
            '\n'
            'JSON body format example:\n'
            '{\n'
            '    "target": "https://blabla.free.beeceptor.com/my/api/path",\n'
            '    "method": "POST",\n'
            '    "headers": {\n'
            '        "Content-Type": "application/json"\n'
            '    },\n'
            '    "payload": {\n'
            '        "data": "Hello Beeceptor"\n'
            '    },\n'
            '    "param": "data"\n'
            '}\n')

        self.send_result(200, message)


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, host='0.0.0.0', port=8000):
    print(f'Server started at port {port}. Press CTRL+C to close the server.')

    server_address = (host, port)

    handler_class.use_http()
    handler_class.use_controllers()

    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server Closed')

run(socketserver.TCPServer, App)
