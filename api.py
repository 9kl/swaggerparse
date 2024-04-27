# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from enum import Enum

import requests
from jinja2 import Environment, FileSystemLoader

from parse import SwaggerDocument


class ResponseDataTypeEnum(Enum):
    ONE = "one"
    MANY = "many"
    PAGE = "page"
    BASE = "base"


class SwaggerPathWrapper(object):
    def __init__(self, paths, schemas, request_schemas, response_schemas):
        self.paths = paths
        self.schemas = schemas
        self.request_schemas = request_schemas
        self.response_schemas = response_schemas


def load_swagger_url(url: str) -> SwaggerDocument:
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        doc = SwaggerDocument(data)
        return doc
    else:
        raise Exception(f'通过{url}获取swagger.json失败')


def load_path_wrapper(swagger_doc: SwaggerDocument,
                      filter_schema_func: callable, filter_path_func: callable) -> SwaggerPathWrapper:
    schemas = [schema for schema in swagger_doc.parse_schema() if filter_schema_func(schema)]
    # 请求涉及到的schema
    request_schemas = set()
    # 响应涉及到的schema
    response_schemas = set()
    # 请求body字段的schema
    request_body_schema = None
    # 响应data字段的schema
    response_data_schema = None

    # 响应类型（one=一条数据、many=多条、page=分页）
    response_data_type = ResponseDataTypeEnum.BASE
    paths = []
    for path in swagger_doc.parse_path():
        if filter_path_func(path):
            for field in path.request.schema.parse_field():
                if field.field_name == 'body':
                    if field.field_type in ('ref', 'array',):
                        request_schemas.add([schema for schema in schemas if schema.name == field.inner_type][0])
                        request_body_schema = field.inner_type
                    else:
                        request_body_schema = field.field_type
                    break

            exists_total_field = False
            for field in path.response.schema.parse_field():
                if field.field_name == 'data':
                    if field.field_type == 'array':
                        response_data_schema = field.inner_type
                        response_data_type = ResponseDataTypeEnum.MANY
                        response_schemas.add([schema for schema in schemas if schema.name == field.inner_type][0])
                    elif field.field_type == 'ref':
                        response_data_schema = field.inner_type
                        response_data_type = ResponseDataTypeEnum.ONE
                        response_schemas.add([schema for schema in schemas if schema.name == field.inner_type][0])
                    else:
                        response_data_schema = field.field_type
                        response_data_type = ResponseDataTypeEnum.BASE
                elif field.field_name == 'total':
                    exists_total_field = True

            if exists_total_field:
                response_data_type = ResponseDataTypeEnum.PAGE

            paths.append({'c': path, 'body_schema': request_body_schema, 'data_schema': response_data_schema,
                          'response_type': response_data_type.value})

    return SwaggerPathWrapper(paths, schemas, request_schemas, response_schemas)


class SwaggerTemplateRender(object):

    def __init__(self, template_dir, filters=None):
        filters = filters or {}
        loader = FileSystemLoader(template_dir)
        env = Environment(loader=loader)
        env.filters.update(filters.copy())
        self.env = env

    def get_template(self, template_name):
        t = self.env.get_template(template_name)
        return t

    def gen_schema_template_file(self, swagger_doc: SwaggerDocument, template_name: str, out_dir: str,
                                 filter_schema_func: callable = None, rename_func: callable = None, **kwargs):
        t = self.get_template(template_name)
        for schema in swagger_doc.parse_schema():
            if filter_schema_func and not filter_schema_func(schema):
                continue

            d = {'schema': schema, 'fields': [field for field in schema.parse_field()]}
            d.update(**kwargs)

            if rename_func:
                out_file_name = rename_func(schema)
            else:
                out_file_name = '%s%s' % (schema.name, '.txt')

            out_file = os.path.join(out_dir, out_file_name)
            out_file_dir = os.path.dirname(out_file)
            if not os.path.exists(out_file_dir):
                os.makedirs(out_file_dir)

            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(t.render(d))

    def gen_singtemplate_file(self, swagger_doc: SwaggerDocument, template_name: str, out_file,
                              filter_schema_func, filter_path_func, **kwargs):
        t = self.get_template(template_name)
        schemas = [schema for schema in swagger_doc.parse_schema() if filter_schema_func(schema)]
        paths = [schema for schema in swagger_doc.parse_path() if filter_path_func(schema)]

        out_file_dir = os.path.dirname(out_file)
        if not os.path.exists(out_file):
            os.makedirs(out_file_dir)

        d = {'schema': schemas, 'paths': paths}
        d.update(**kwargs)

        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(t.render(d))
