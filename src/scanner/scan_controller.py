import json
import os
import subprocess
from sqlalchemy import create_engine, text
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors

SONARQUBE_ADDRESS = os.environ.get('SONARQUBE_ADDRESS', '')
POSTGRES_USER = os.environ.get('POSTGRES_USER', '')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'sonar')

class ScanController():
  def init_scan(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if not 'key' in data or not isinstance(data['key'], str):
        raise Exception('"key" must be a string')
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
  
  def scan_report(self, ctx, static_dir):
    data = ctx.http.get_request_query_params(ctx)

    try:
      if not 'key' in data or not isinstance(data['key'], str):
        raise Exception('"key" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    project_key = data['key']

    try:
      issues = self.__get_issues_from_db(ctx, project_key)

      report_path = os.path.join(static_dir, f'{project_key}_report.pdf')

      self.__generate_pdf(ctx, issues, report_path, project_key)

      ctx.http.send_response(ctx, 200)
      ctx.http.send_header(ctx, 'Content-type', 'application/pdf')
      ctx.http.end_headers(ctx)

      with open(report_path, 'rb') as file:
        return ctx.http.serve_file(ctx, file)
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

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

    return ctx.http.send_result(ctx)

  def __get_issues_from_db(self, ctx, project_key):
    try:
      engine = create_engine(f'postgresql+pg8000://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
      with engine.connect() as conn:
        query = """
        SELECT i.severity, i.message, i.line, c.path
        FROM components c
            JOIN issues i ON i.component_uuid = c.uuid
        WHERE c.kee like :project_key
        """
        result = conn.execute(text(query), {'project_key': f'{project_key}:%'})

        return result.fetchall()
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

  def __generate_pdf(self, ctx, issues, report_path, project_key):
    try:
      doc = SimpleDocTemplate(report_path, pagesize=letter)
      styles = getSampleStyleSheet()
      flowables = []

      # Title
      title = Paragraph(f'Security Issues Report for Project: {project_key}', styles['Title'])
      flowables.append(title)
      flowables.append(Paragraph('<br/><br/>', styles['Normal']))

      # Table
      table_data = [['Severity', 'Message', 'Line', 'Path']]
      for issue in issues:
          table_data.append(list(issue))

      table = Table(table_data)
      table.setStyle(TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
          ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
          ('GRID', (0, 0), (-1, -1), 1, colors.black),
      ]))

      flowables.append(table)
      doc.build(flowables)
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)
