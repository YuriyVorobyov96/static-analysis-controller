class IssuesController():
  def get_issues(self, ctx):
    data = ctx.http.get_request_query_params(ctx)

    try:
      if data:
        if 'name' in data and not isinstance(data['name'], str):
            raise Exception('"name" must be a string')
        if 'status' in data:
          if not isinstance(data['status'], str):
            raise Exception('"status" must be a string')
          if data['status'] not in ['OPEN', 'CONFIRMED', 'FALSE_POSITIVE', 'ACCEPTED', 'FIXED']:
            raise Exception('"status" must be one of [OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED]')
        if 'type' in data:
          if not isinstance(data['type'], str):
            raise Exception('"type" must be a string')
          if data['type'] not in ['MAINTAINABILITY', 'RELIABILITY', 'SECURITY']:
            raise Exception('"type" must be one of [MAINTAINABILITY, RELIABILITY, SECURITY]')
        if 'page' in data:
          try:
            data['page'] = int(data['page'])
          except:
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
