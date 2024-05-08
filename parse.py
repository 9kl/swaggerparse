from fields import StringField, NumberField, BooleanField, IntegerField, ObjectField, ArrayField, RefField, UnknownField


class SwaggerDocument(object):
    def __init__(self, doc):
        self.info = doc['info']
        self.components = doc['components']
        self.schemas = self.components['schemas']
        self.openapi = doc['openapi']
        self.paths = doc['paths']
        self.servers = doc['servers']

    @property
    def title(self):
        return self.info['title']

    @property
    def version(self):
        return self.info['version']

    @property
    def description(self):
        return self.info['description']

    def parse_schema(self):
        for schema_name, schema in self.schemas.items():
            yield SwaggerSchema(schema_name, schema)

    def parse_path(self):
        for path, path_props in self.paths.items():
            for method, method_props in path_props.items():
                yield SwaggerPath(path, method, method_props)


class SwaggerSchema(object):
    def __init__(self, name, schema):
        self.name = name
        self.properties = schema['properties']
        self.type = schema['type']
        self.required_fields = schema.get('required', [])

    def parse_field(self):
        for field_name, field_props in self.properties.items():
            required = field_name in self.required_fields
            if 'type' in field_props:
                field_type = field_props['type']
                if field_type == 'string':
                    yield StringField(field_name, required, field_props)
                elif field_type == 'number':
                    yield NumberField(field_name, required, field_props)
                elif field_type == 'integer':
                    yield IntegerField(field_name, required, field_props)
                elif field_type == 'boolean':
                    yield BooleanField(field_name, required, field_props)
                elif field_type == 'object':
                    yield ObjectField(field_name, required, field_props)
                elif field_type == 'array':
                    yield ArrayField(field_name, required, field_props)
                else:
                    yield UnknownField(field_name, required, field_props)
            elif '$ref' in field_props:
                yield RefField(field_name, required, field_props)
            elif 'allOf' in field_props:
                yield RefField(field_name, required, field_props)
            else:
                yield UnknownField(field_name, required, field_props)

    def __repr__(self):
        return self.name


class SwaggerPath(object):
    def __init__(self, uri, method, method_props):
        self.uri = uri
        self.method = method
        self.props = method_props

    @property
    def tags(self):
        return self.props['tags']

    @property
    def summary(self):
        return self.props['summary']

    @property
    def request(self):
        return SwaggerRequest(self.props['requestBody'])

    @property
    def response(self):
        return SwaggerResponse(self.props['responses'])


class SwaggerRequest(object):
    def __init__(self, request_body):
        self.request_body = request_body
        self.schema = SwaggerSchema('', request_body['content']['application/json']['schema'])

    @property
    def content_type(self):
        return list(self.request_body['content'].keys())[0]

    def get_field(self, field_name):
        fields = [field for field in self.schema.parse_field() if field.field_name == field_name]
        if fields:
            return fields[0]
        else:
            return None

    def __str__(self):
        return f'SwaggerRequest content_type: {self.content_type}, schema:{self.schema}'


class SwaggerResponse(object):
    def __init__(self, responses):
        self.responses = responses
        self.schema = SwaggerSchema('', responses['200']['content']['application/json']['schema'])

    @property
    def content_type(self) -> str:
        return list(self.responses['200']['content'].keys())[0]

    def __str__(self):
        return f'SwaggerResponse content_type: {self.content_type}, schema:{self.schema}'
