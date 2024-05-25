import os

class AppController:
  def help_message(self, ctx):
    message = ('Welcome to Analysis Controller\n'
      'To perform actions send requests to specified routes\n'
      '\n'
      'Documentation available via GET /docs/openapi'
      '\n')

    ctx.http.send_result(ctx, 200, message)

  def get_openapi_documentation(self, ctx, doc_dir):
    try:
      path = doc_dir / 'index.html'
      with open(path, 'rb') as file:
        ctx.http.send_response(ctx, 200)
        ctx.http.send_header(ctx, 'Content-type', 'text/html')
        ctx.http.end_headers(ctx)
        return ctx.http.serve_file(ctx, file)
    except FileNotFoundError:
      return ctx.http.send_not_found_error(ctx, 'Documentation not found')
    except Exception as err:
      print('Read documentation index.html error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Serve file error')

  def get_openapi_file(self, ctx, doc_dir, file_name):
    try:
      with open(os.path.join(doc_dir, file_name), 'rb') as file:
        ctx.http.send_response(ctx, 200)
        ctx.http.send_header(ctx, 'Content-type', 'text/plain')
        ctx.http.end_headers(ctx)
        return ctx.http.serve_file(ctx, file)
    except FileNotFoundError:
      return ctx.http.send_not_found_error(ctx, 'Documentation not found')
    except Exception as err:
      print('Read documentation openapi.yaml error:', err)
      return ctx.http.send_bad_request_error(ctx, 'Serve file error')

  def serve_static(self, ctx, dir, file_name):
    try:
      with open(os.path.join(dir, file_name), 'rb') as file:
        ctx.http.send_response(ctx, 200)
        if ctx.path.endswith('.html'):
          ctx.http.send_header(ctx, 'Content-type', 'text/html')
        if ctx.path.endswith('.css'):
          ctx.http.send_header(ctx, 'Content-type', 'text/css')
        if ctx.path.endswith('.css'):
          ctx.http.send_header(ctx, 'Content-type', 'text/png')
        elif ctx.path.endswith('.js'):
          ctx.http.send_header(ctx, 'Content-type', 'application/javascript')
        ctx.http.end_headers(ctx)
        return ctx.http.serve_file(ctx, file)
    except FileNotFoundError:
      print('File not found:', os.path.join(dir, file_name))
      return ctx.http.send_not_found_error(ctx, 'File not found')
    except Exception as err:
      print('Read file error:', os.path.join(dir, file_name), err)
      return ctx.http.send_bad_request_error(ctx, 'Serve file error')
