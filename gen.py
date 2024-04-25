# encoding: utf-8

import os

from api import SwaggerTemplateRender, load_path_wrapper, load_swagger_url
from filters import __filters__
from parse import SwaggerSchema, SwaggerPath

base_dir = os.path.dirname(__file__)
template_dir = os.path.join(base_dir, 'templates')
root_dir = os.path.join(base_dir, 'output')

swagger_url = 'http://192.168.102.40:9900/api/doc/swagger.json'
root_name = 'cn.linkeddt.wisdomwatersystem'
app_name = 'irrms'
package_name = 'monitor'


def gen_java_entity():
    api = SwaggerTemplateRender(template_dir, __filters__)
    _out_dir = os.path.join(root_dir, 'entitys')

    def rename(schema: SwaggerSchema):
        return f'{schema.name}.java'

    def filter_schema(schema: SwaggerSchema):
        return 'Monitor' in schema.name and 'Query' not in schema.name

    swagger_doc = load_swagger_url(swagger_url)
    api.gen_schema_template_file(swagger_doc, 'java_entity.jinja2', _out_dir,
                                 filter_schema, rename,
                                 **{'root_name': root_name, 'app_name': app_name, 'package_name': package_name})


def gen_java_entity_query():
    api = SwaggerTemplateRender(template_dir, __filters__)
    _out_dir = os.path.join(root_dir, 'entitys', 'query')

    def rename(schema: SwaggerSchema):
        return f'{schema.name}.java'

    def filter_schema(schema: SwaggerSchema):
        return 'Monitor' in schema.name and 'Query' in schema.name

    swagger_doc = load_swagger_url(swagger_url)
    api.gen_schema_template_file(swagger_doc, 'java_entity_query.jinja2', _out_dir,
                                 filter_schema, rename,
                                 **{'root_name': root_name, 'app_name': app_name, 'package_name': package_name})


def gen_android_api():
    api = SwaggerTemplateRender(template_dir, __filters__)

    def filter_path(path: SwaggerPath):
        return '/api/monitor/monitor_canal/' in path.uri

    def filter_schema(schema: SwaggerSchema):
        return True

    def _gen_android_service(schemas, paths, request_schemas, response_schemas, out_dir, file_name):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = api.get_template('android_service.jinja2')
        d = {'schemas': schemas, 'paths': paths, 'request_schemas': request_schemas,
             'response_schemas': response_schemas}
        d.update({'root_name': root_name, 'app_name': app_name, 'package_name': package_name, 'class_name': 'MonitorCanal'})

        out_file = os.path.join(out_dir, file_name)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(t.render(d))

    def _gen_android_repo(schemas, paths, request_schemas, response_schemas, out_dir, file_name):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = api.get_template('android_repo.jinja2')
        d = {'schemas': schemas, 'paths': paths, 'request_schemas': request_schemas,
             'response_schemas': response_schemas}
        d.update({'root_name': root_name, 'app_name': app_name, 'package_name': package_name, 'class_name': 'MonitorCanal'})

        out_file = os.path.join(out_dir, file_name)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(t.render(d))

    def _gen_java_entity(t, schemas, out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for schema in schemas:
            d = {'schema': schema, 'fields': [field for field in schema.parse_field()]}
            d.update({'root_name': root_name, 'app_name': app_name, 'package_name': package_name})
            out_file = os.path.join(out_dir, f'{schema.name}.java')
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(t.render(d))

    swagger_doc = load_swagger_url(swagger_url)
    wrapper = load_path_wrapper(swagger_doc, filter_schema_func=filter_schema, filter_path_func=filter_path)

    _gen_java_entity(api.get_template('java_entity_query.jinja2'), wrapper.request_schemas,
                     os.path.join(root_dir, 'entitys', 'query'))

    _gen_java_entity(api.get_template('java_entity.jinja2'), wrapper.response_schemas,
                     os.path.join(root_dir, 'entitys'))

    _gen_android_service(wrapper.schemas, wrapper.paths, wrapper.request_schemas, wrapper.response_schemas,
                         os.path.join(root_dir, 'services'), 'MonitorCanalService.java')

    _gen_android_repo(wrapper.schemas, wrapper.paths, wrapper.request_schemas, wrapper.response_schemas,
                      os.path.join(root_dir, 'repos'), 'MonitorCanalRepo.java')


if __name__ == '__main__':
    lst = ['/api/monitor/monitor_canal/', '/api/monitor/monitor_canal/', '/api/monitor/monitor_canal/', '/api/monitor/monitor_canal/']
    for item in lst:
        gen_android_api(item)

    # gen_java_entity()
    # gen_java_entity_query()
