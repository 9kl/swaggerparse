# -*- coding: utf-8 -*-


def decapitalize(str, upper_rest=False):
    return str[:1].lower() + (str[1:].upper() if upper_rest else str[1:])


def class_name(value):
    lst = value.split('_')
    lst = [item[0].upper() + item[1:].lower() for item in lst]
    return ''.join(lst)


def class_name1(value):
    lst = value.split('_')
    lst = [item[0].upper() + item[1:] for item in lst]
    return ''.join(lst)


def js_name(value):
    return decapitalize(class_name(value))


def parame_name(value):
    value = value.lower()
    if value in ('id',):
        return '_%s' % value
    return value


def form_field_validat(value, length, precision):
    if length is None:
        return ''

    data_type = _get_group_datatype(value)
    if data_type in ('varchar',):
        return ', max_length=%s' % length
    elif data_type in ('numeric', 'int',):
        if precision:
            return ', max_digits=%s, decimal_places=%s' % (length, precision)
        else:
            return ', max_value=%s, min_value=%s' % ((int('1' + '0' * int(length)) - 1), 0)
    return ''


def _get_group_datatype(value):
    """ 获取分组数据类型，如varchar与text同属于varchar类型?
    """
    try:
        index = value.rfind('(')
        data_type = (value if index == -1 else value[:index]).lower()

        if data_type.find('char') != -1 or data_type.find('text') != -1 or data_type.find(
                'clob') != -1 or data_type.find('blob') != -1:
            return 'varchar'
        elif data_type.find('numeric') != -1 or data_type.find('number') != -1:
            return 'numeric'
        elif data_type.find('int') != -1:
            return 'int'
        elif data_type.find('float') != -1:
            return 'float'
        elif data_type.find('timestamp') != -1 or data_type.find('time') != -1:
            return 'datetime'
        elif data_type.find('date') != -1:
            return 'date'
        elif data_type.find('bit') != -1:
            return 'bool'
        elif data_type.find('uniqueidentifier') != -1:
            return 'uniqueidentifier'
        elif data_type.find('jsonb') != -1 or data_type.find('json') != -1:
            return 'jsonb'
        return value
    except Exception as ex:
        print(value)


def form_fieldclass(value):
    """ 根据PDM中的字段的数据类型获得生成Form模板中字段的Field class
    """
    d = {'varchar': 'CharField', 'uniqueidentifier': 'CharField', 'datetime': 'DateTimeField', 'date': 'DateField',
         'numeric': 'DecimalField', 'int': 'IntegerField', 'bool': 'BooleanField'}

    data_type = _get_group_datatype(value)

    if data_type == 'numeric' and value.rfind(',') == -1:
        data_type = 'int'
    return d.get(data_type, value)


def serializer_fieldclass(value):
    """根据PDM中的字段的数据类型获得生成Serializer模板中字段的Field class
    """
    d = {'varchar': 'CharField', 'uniqueidentifier': 'CharField', 'datetime': 'DateTimeField',
         'numeric': 'DecimalField', 'int': 'IntegerField', 'bool': 'BooleanField'}

    """
    d = {'varchar': 'CharField', 'uniqueidentifier': 'CharField', 'datetime': 'CharField',
         'numeric': 'DecimalField', 'int': 'IntegerField', 'bool': 'BooleanField'}
    """

    data_type = _get_group_datatype(value)

    if data_type == 'numeric' and value.rfind(',') == -1:
        data_type = 'int'
    return d.get(data_type, value)


def schema_fieldclass(value):
    """ 根据PDM中的字段的数据类型获得生成Schema模板中字段的Field class
    """

    d = {'varchar': 'fields.Str', 'uniqueidentifier': 'fields.Str', 'datetime': 'PgDateTimeField',
         'numeric': 'fields.Decimal', 'int': 'fields.Int', 'bool': 'fields.Bool', 'jsonb': 'fields.Dict',
         'date': 'PgDateField'}

    data_type = _get_group_datatype(value)

    if data_type == 'numeric' and value.rfind(',') == -1:
        data_type = 'int'
    return d.get(data_type, value)


def schema_field_validate(value, length, precision):
    if length is None:
        return ''

    data_type = _get_group_datatype(value)
    if data_type in ('varchar',):
        return ', validate=validate.Length(max=%s)' % length
    elif data_type in ('numeric', 'int',):
        if precision:
            return ', places=%s, validate=validate.Range(min=%s, max=%s, max_inclusive=False)' % (
                precision, 0, (int('1' + '0' * int(int(length) - int(precision)))))
        else:
            return ', validate=validate.Range(min=%s, max=%s)' % (0, (int('1' + '0' * int(length)) - 1))
    return ''


def vue_field_validate(value, length, precision):
    if length is None:
        return ''

    data_type = _get_group_datatype(value)
    if data_type in ('numeric', 'int',):
        if precision:
            return 'min="%s" max="%s" step="%s"' % (
                0, (int('1' + '0' * int(int(length) - int(precision)))), 1.0 / int('1' + '0' * int(precision)))
        else:
            return 'min="%s" max="%s" step="%s"' % (0, (int('1' + '0' * int(length)) - 1), 1)
    return ''


def vue_table_column_align(value):
    data_type = _get_group_datatype(value)
    if data_type in ('numeric', 'int', 'float',):
        return 'right'
    elif data_type in ('bool', 'datetime'):
        return 'center'
    else:
        return 'left'


def table_th_width(value):
    """ table th width 根据表头文字的长度获取默认宽度"""
    return len(value) * 20


def py_fun_parame(value, data_type):
    value = value.lower()
    if value in ('id',):
        value = '_%s' % value

    data_type = _get_group_datatype(data_type)
    if data_type in ('varchar', 'uniqueidentifier',):
        return '%s: %s' % (value, 'str')
    elif data_type in ('numeric', 'float',):
        return '%s: %s' % (value, 'float')
    elif data_type in ('int',):
        return '%s: %s' % (value, 'int')
    elif data_type in ('datetime',):
        return '%s: %s' % (value, 'datetime')
    elif data_type in ('bool',):
        return '%s: %s' % (value, 'bool')
    return value


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
    method_name = to_camel_case(parts[-1])
    return method_name


__filters__ = {
    'class_name': class_name,
    'js_name': js_name,
    'parame_name': parame_name,
    'form_fieldclass': form_fieldclass,
    'form_field_validat': form_field_validat,
    'serializer_fieldclass': serializer_fieldclass,
    'schema_fieldclass': schema_fieldclass,
    'schema_field_validate': schema_field_validate,
    'vue_field_validate': vue_field_validate,
    'vue_table_column_align': vue_table_column_align,
    'py_fun_parame': py_fun_parame,
    'JavaClass': to_java_class,
    'PascalCase': to_pascal_case,
    'CamelCase': to_camel_case,
    'UrlToClassName': to_path_url_class_name,
    'UrlToMethodName': to_path_url_method_name
}
