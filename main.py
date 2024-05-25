import sys
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

sys.path.append('./src/www')
sys.path.append('./src/scanner')

from http_server import HTTP
from project_controller import ProjectController
from token_controller import TokenController

class App(BaseHTTPRequestHandler):
    @classmethod
    def use_http(cls):
      cls.http = HTTP()

    @classmethod
    def use_controllers(cls):
      cls.project_controller = ProjectController()
      cls.token_controller = TokenController()

    def do_GET(self):
        if self.path == '/help':
            return self.__help_message()

        if self.path == '/scanner/project/search':
          return self.project_controller.search_project(self)

        if self.path == '/scanner/scan/issues':
            return self.get_issues()

        return self.http.send_not_found_error(self)

    def do_POST(self):
      if self.path == '/scanner/project/create':
        return self.project_controller.create_project(self)

      if self.path == '/scanner/token/create':
        return self.token_controller.create_analysis_token(self)

      if self.path == '/scanner/scan/init':
        return self.init_scan()

      return self.http.send_not_found_error(self)

    def init_scan(self):
      data = self.get_request_body()

      try:
        if data:
          if not 'source' in data or not isinstance(data['source'], str):
              raise Exception('"source" must be a string')
          if not 'token' in data or not isinstance(data['token'], str):
              raise Exception('"token" must be a string')
      except Exception as err:
        return self.send_bad_request_error(err)

      try:
        cmd = f"sonar-scanner \
                      -Dsonar.projectKey=test \
                      -Dsonar.sources={data['source']} \
                      -Dsonar.host.url=http://localhost:9000 \
                      -Dsonar.token={data['token']}"

        subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
      except Exception as err:
        return self.send_bad_request_error(err)

      return self.send_result(200)

    def get_issues(self):
      data = self.get_request_body()

      try:
        if data:
          if 'name' in data and not isinstance(data['name'], str):
            raise Exception('"name" must be a string')
          if 'status' in data and not isinstance(data['status'], str):
            raise Exception('"status" must be a string')
          if 'type' in data and not isinstance(data['type'], str):
            raise Exception('"type" must be a string')
          if 'page' in data and not isinstance(data['page'], int):
            raise Exception('"page" must be an integer')
      except Exception as err:
        return self.send_bad_request_error(err)

      payload = dict()

      if 'name' in data:
          payload['components'] = data['name']
      if 'status' in data:
          payload['issueStatuses'] = data['status']
      if 'type' in data:
          payload['impactSoftwareQualities'] = data['type']
      if 'page' in data:
          payload['p'] = data['page']

      self.send_request('GET', 'http://localhost:9000/api/issues/search', payload)

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
