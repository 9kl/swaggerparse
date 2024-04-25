from api import load_swagger_url

if __name__ == '__main__':
    swagger = load_swagger_url('http://192.168.102.40:9900/api/doc/swagger.json')
    schemas = [schema for schema in swagger.parse_schema()]

    for path in swagger.parse_path():
        if path.uri == '/api/irr/baseinfo/irr_district/detail':
            print(f'path:{path.uri}')
            print(f'summary:{path.summary}')
            print(f'tags:{path.tags}')
            print(f'method:{path.method}')
            print(f'request:')
            for field in path.request.schema.parse_field():
                print(field)

            print(f'response:')
            for field in path.response.schema.parse_field():
                print(field)
