import subprocess

class ScanController():
  def get_issues(self, ctx):
    data = ctx.http.get_request_query_params(ctx)

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
      return ctx.http.send_bad_request_error(ctx, err)

    payload = dict()

    if 'name' in data:
      payload['components'] = data['name']
    if 'status' in data:
      payload['issueStatuses'] = data['status']
    if 'type' in data:
      payload['impactSoftwareQualities'] = data['type']
    if 'page' in data:
      payload['p'] = data['page']

    ctx.http.send_request(ctx, 'GET', 'http://localhost:9000/api/issues/search', payload)

  def init_scan(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if data:
        if not 'source' in data or not isinstance(data['source'], str):
          raise Exception('"source" must be a string')
        if not 'token' in data or not isinstance(data['token'], str):
          raise Exception('"token" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    try:
      cmd = f"sonar-scanner \
                    -Dsonar.projectKey=test \
                    -Dsonar.sources={data['source']} \
                    -Dsonar.host.url=http://localhost:9000 \
                    -Dsonar.token={data['token']}"

      subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    return ctx.http.send_result(ctx)
