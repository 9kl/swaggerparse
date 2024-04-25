# -*- coding: utf-8 -*-


def to_java_class(value):
    if value in ('number',):
        return 'Double'

    if value in ('string', 'object',):
        return 'String'

    if value in ('integer',):
        return 'Integer'

    if value in ('boolean',):
        return 'Boolean'

    return value


def to_pascal_case(value):
    """
    大驼峰命名
    :param value:
    :return:
    """
    parts = value.split('_')
    # 将每个部分的首字母大写，并连接起来
    camel_case = ''.join(part.capitalize() for part in parts)
    return camel_case


def to_camel_case(value):
    """
    小驼峰命名
    :param value:
    :return:
    """
    parts = value.split('_')
    # 处理第一个单词，保持小写，然后将后续的单词首字母大写
    camel_case = parts[0] + ''.join(part.capitalize() for part in parts[1:])
    return camel_case


def to_path_url_class_name(value, index):
    """
    通过path的url获取类名
    :param value:
    :param index:
    :return:
    """
    parts = value.split('/')
    file_name = to_pascal_case(parts[index])
    return f'{file_name}Service.java'


def to_path_url_method_name(value):
    """
    通过path的url获取方法名
    :param value:
    :return:
    """
    parts = value.split('/')
    new_parts = '_'.join(parts[4:])
    method_name = to_camel_case(new_parts)
    return method_name


__filters__ = {
    'JavaClass': to_java_class,
    'PascalCase': to_pascal_case,
    'CamelCase': to_camel_case,
    'UrlToClassName': to_path_url_class_name,
    'UrlToMethodName': to_path_url_method_name
}
