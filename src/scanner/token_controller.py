import os

SONARQUBE_ADDRESS = os.environ.get('SONARQUBE_ADDRESS', '')

class TokenController():
  def create_analysis_token(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if data:
        if not 'key' in data or not isinstance(data['key'], str):
          raise Exception('"key" must be a string')
        if not 'name' in data or not isinstance(data['name'], str):
          raise Exception('"name" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    payload = { 'projectKey': data['key'], 'name': data['name'] }

    payload['type'] = 'PROJECT_ANALYSIS_TOKEN'

    ctx.http.send_request(ctx, 'POST', f'{SONARQUBE_ADDRESS}/api/user_tokens/generate', payload)
