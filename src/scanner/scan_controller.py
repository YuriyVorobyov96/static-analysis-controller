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
                    -Dsonar.projectKey=test \
                    -Dsonar.sources={data['source']} \
                    -Dsonar.host.url=http://localhost:9000 \
                    -Dsonar.token={data['token']}"

      subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    return ctx.http.send_result(ctx)
