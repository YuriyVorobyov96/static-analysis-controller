import json
import os
import requests
from urllib.parse import urlparse, parse_qs

API_KEY = os.environ.get('API_KEY', 'AUTH-TOKEN')
SONARQUBE_TOKEN = os.environ.get('SONARQUBE_TOKEN', '')

class HTTPUtils():
  def send_request(self, ctx, method, target, payload):
    try:
      self.__check_auth(ctx)
      self.__check_json_request_content_type(ctx)
    except Exception as err:
      return self.send_bad_request_error(ctx, err)

    try:
      headers = { 'Authorization': SONARQUBE_TOKEN }

      data = '?'

      for i, (key, value) in enumerate(payload.items()):
        data += f'{key}={value}'

        if i != len(payload) - 1:
          data += '&'

      target += data

      response = self.__sent_http_request(target, method, headers, data)

      response_info = self.__get_response_info(response)
      print(response_info)

      return self.send_result(ctx, response.status_code, response.text)
    except Exception as err:
      return self.__send_internal_server_error(ctx, err)

  def send_not_found_error(self, ctx):
    self.__do_response(ctx, 404, json.dumps({ 'err': 'Invalid path' }))

  def send_bad_request_error(self, ctx, err):
    error = { 'err': str(err) }
    self.__do_response(ctx, 400, json.dumps(error))

  def get_request_body(self, ctx):
    content_len = int(ctx.headers.get('Content-Length'))
    post_body = ctx.rfile.read(content_len)

    try:
      body = json.loads(post_body)
    except:
      return self.send_bad_request_error(ctx, 'Invalid JSON')

    return { k.lower(): v for k, v in body.items() }

  def get_request_query_params(self, ctx):
    try:
      query_params = parse_qs(urlparse(ctx.path).query)

      for (key, value) in query_params.items():
        query_params[key] = value[0]

      return query_params
    except:
      return self.send_bad_request_error(ctx, 'Invalid query params format')

  def get_path_url(self, ctx):
    try:
      parsed_path = urlparse(ctx.path)

      return parsed_path.path
    except:
      return self.send_bad_request_error(ctx, 'Invalid URL format')

  def send_result(self, ctx, code=200, result=json.dumps({ 'msg': 'OK' })):
    self.__do_response(ctx, code, result)

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

  def __do_response(self, ctx, status_code=200, content=''):
    ctx.send_response(status_code)

    try:
      json.loads(content)
      ctx.send_header('Content-type', 'application/json')
    except:
      ctx.send_header('Content-type', 'text/plain')

    ctx.end_headers()
    response = bytes(f'{content}', 'utf8')
    ctx.wfile.write(response)

  def __send_internal_server_error(self, ctx, err):
    print(err)
    self.__do_response(ctx, 500, json.dumps({ 'err': 'Internal server error' }))

  def __get_content_type_header(self, ctx):
    return ctx.headers.get('Content-Type')

  def __is_json_content_type(self, content_type):
    return content_type == 'application/json'

  def __check_auth(self, ctx):
    if (ctx.headers.get('Authorization') != API_KEY):
      raise Exception('Invalid authorization token')
  
  def __check_json_request_content_type(self, ctx):
    content_type = self.__get_content_type_header(ctx)

    if not self.__is_json_content_type(content_type):
      raise Exception('Invalid Header Type: Send JSON\nFor more info send GET request to "/help" path')
