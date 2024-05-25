class ProjectController():
  def create_project(self, ctx):
    data = ctx.http.get_request_body(ctx)

    try:
      if data:
        if not 'key' in data or not isinstance(data['key'], str):
          raise Exception('"key" must be a string')
        if not 'name' in data or not isinstance(data['name'], str):
          raise Exception('"name" must be a string')
        if 'mainBranch' in data and not isinstance(data['mainBranch'], str):
          raise Exception('"mainBranch" must be a string')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    payload = { 'project': data['key'], 'name': data['name'] }

    if 'mainBranch' in data:
      payload['mainBranch'] = data['mainBranch']

    ctx.http.send_request(ctx, 'POST', 'http://localhost:9000/api/projects/create', payload)

  def search_project(self, ctx):
    data = ctx.http.get_request_query_params(ctx)

    try:
      if data:
        if 'query' in data and not isinstance(data['query'], str):
          raise Exception('"query" must be a string')
        if 'page' in data:
          try:
            data['page'] = int(data['page'])
          except:
            raise Exception('"page" must be an integer')
    except Exception as err:
      return ctx.http.send_bad_request_error(ctx, err)

    payload = dict()

    if 'query' in data:
      payload['q'] = data['query']
    if 'page' in data:
      payload['p'] = data['page']

    ctx.http.send_request(ctx, 'GET', 'http://localhost:9000/api/projects/search', payload)
