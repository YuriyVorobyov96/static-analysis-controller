import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class HTTP(BaseHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

  def send_request(self, method, target, payload):
      try:
          self.__check_json_request_content_type()
      except Exception as err:
          return self.send_bad_request_error(err)

      try:
          headers = { "Authorization": "Bearer squ_1bb3dc40d54c5d1df2b5255aa530bdc2820bfb1b" }

          data = '?'

          for i, (key, value) in enumerate(payload.items()):
            data += f'{key}={value}'

            if i != len(payload) - 1:
              data += '&'

          target += data

          response = self.__sent_http_request(target, method, headers, data)

          response_info = self.__get_response_info(response)
          print(response_info)

          return self.send_result(response.status_code, response.text)
      except Exception as err:
          return self.__send_internal_server_error(err)

  def get_request_body(self):
    content_len = int(self.headers.get('Content-Length'))
    post_body = self.rfile.read(content_len)

    body = json.loads(post_body)

    return { k.lower(): v for k, v in body.items() }

  def send_not_found_error(self):
      self.__do_response(404, json.dumps({ 'err': 'Invalid path' }))

  def send_bad_request_error(self, err):
      error = { 'err': str(err) }
      self.__do_response(400, json.dumps(error))

  def get_request_body(self):
      content_len = int(self.headers.get('Content-Length'))
      post_body = self.rfile.read(content_len)

      body = json.loads(post_body)

      return { k.lower(): v for k, v in body.items() }

  def __sent_http_request(self, target, method, headers, payload):
      match method.upper():
          case 'GET':
              return requests.get(target, headers=headers, data=payload)
          case 'POST':
              return requests.post(target, headers=headers, data=payload)
          case 'PUT':
              return requests.put(target, headers=headers, data=payload)
          case 'PATCH':
              return requests.patch(target, headers=headers, data=payload)
          case 'DELETE':
              return requests.delete(target, headers=headers, data=payload)

  def __get_response_info(self, response):
      return (f'[#] Response status code: {response.status_code}\n'
          f'[#] Response headers: {json.dumps(dict(response.headers), indent=4, sort_keys=True)}\n'
          f'[#] Response content:\n{response.text}')

  def __do_response(self, status_code=200, content=''):
      self.send_response(status_code)

      try:
        json.loads(content)
        self.send_header('Content-type', 'application/json')
      except:
        self.send_header('Content-type', 'text/plain')

      self.end_headers()
      response = bytes(f'{content}', 'utf8')
      self.wfile.write(response)

  def __send_internal_server_error(self, err):
      print(err)
      self.__do_response(500, json.dumps({ 'err': 'Internal server error' }))

  def send_result(self, code, result):
      self.__do_response(code, result)

  def __get_content_type_header(self):
      return self.headers.get('Content-Type')

  def __is_json_content_type(self, content_type):
      return content_type == 'application/json'
  
  def __check_json_request_content_type(self):
      content_type = self.__get_content_type_header()

      if not self.__is_json_content_type(content_type):
          raise Exception('Invalid Header Type: Send JSON\nFor more info send GET request to "/help" path')
