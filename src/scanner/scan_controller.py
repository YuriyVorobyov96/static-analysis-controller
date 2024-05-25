import json
import os
import subprocess

SONARQUBE_ADDRESS = os.environ.get('SONARQUBE_ADDRESS', '')

class ScanController():
  def init_scan(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if not 'source' in data or not isinstance(data['source'], str):
        raise Exception('"source" must be a string')
      if not 'token' in data or not isinstance(data['token'], str):
        raise Exception('"token" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    try:
      cmd = f"sonar-scanner \
                    -Dsonar.projectKey={data['key']} \
                    -Dsonar.sources={data['source']} \
                    -Dsonar.host.url={SONARQUBE_ADDRESS} \
                    -Dsonar.token={data['token']}"

      subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    return ctx.http.send_result(ctx)

  def full_analysis(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if not 'key' in data or not isinstance(data['key'], str):
        raise Exception('"key" must be a string')
      if not 'name' in data or not isinstance(data['name'], str):
        raise Exception('"name" must be a string')
      if 'mainBranch' in data and not isinstance(data['mainBranch'], str):
        raise Exception('"mainBranch" must be a string')
      if not 'source' in data or not isinstance(data['source'], str):
        raise Exception('"source" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    token = ''

    try:
      project_creation_payload = { 'project': data['key'], 'name': data['name'] }

      if 'mainBranch' in data:
        project_creation_payload['mainBranch'] = data['mainBranch']

      ctx.http.send_request(ctx, 'POST', f'{SONARQUBE_ADDRESS}/api/projects/create', project_creation_payload, is_internal=True)
    except Exception as err:
      print('Project creation error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Project creation error')

    try:
      token_payload = { 'projectKey': data['key'], 'name': data['name'] }

      token_payload['type'] = 'PROJECT_ANALYSIS_TOKEN'

      token_info_response = ctx.http.send_request(ctx, 'POST', f'{SONARQUBE_ADDRESS}/api/user_tokens/generate', token_payload, is_internal=True)
      token_info = json.loads(token_info_response)
      token = token_info.get('token', '')
    except Exception as err:
      print('Token creation error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Token creation error')

    try:
      cmd = f"sonar-scanner -X \
                    -Dsonar.projectKey={data['key']} \
                    -Dsonar.sources={data['source']} \
                    -Dsonar.host.url={SONARQUBE_ADDRESS} \
                    -Dsonar.token={token}"

      subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
    except Exception as err:
      print('Sonar-scanner error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Sonar-scanner error')

    try:
      payload = {
        'components': data['key'],
        'issueStatuses': 'OPEN',
        'impactSoftwareQualities': 'SECURITY',
        'p': 1,
        'ps': 500,
      }

      all_issues = []

      while True:
        response = ctx.http.send_request(ctx, 'GET', f'{SONARQUBE_ADDRESS}/api/issues/search', payload, is_internal=True)
        data = json.loads(response)
        issues = data.get('issues', [])

        if not issues:
          break

        all_issues.extend(issues)

        payload['p'] += 1

      return ctx.http.send_result(ctx, 200, json.dumps(all_issues))
    except Exception as err:
      print('Sonar error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Sonar error')
