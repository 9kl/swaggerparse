from abc import ABCMeta, abstractmethod


class FieldABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def field_name(self) -> str:
        pass

    @property
    @abstractmethod
    def field_type(self) -> str:
        pass

    @property
    @abstractmethod
    def field_required(self) -> bool:
        pass

    @property
    @abstractmethod
    def field_nullable(self) -> bool:
        pass

    @property
    @abstractmethod
    def field_desc(self) -> str:
        pass

    @property
    @abstractmethod
    def field_props(self) -> str:
        pass


class FieldBase(FieldABC):

    def __init__(self, field_name, field_type, field_required, field_props):
        self._field_name = field_name
        self._field_type = field_type
        self._field_props = field_props
        self._field_required = field_required
        self._field_nullable = field_props.get('nullable', False)
        self._field_desc = field_props.get('description', field_name)

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def field_type(self) -> str:
        return self._field_type

    @property
    def field_required(self) -> bool:
        return self._field_required

    @property
    def field_nullable(self) -> bool:
        return self._field_nullable

    @property
    def field_desc(self) -> str:
        return self._field_desc

    @property
    def field_props(self) -> dict:
        return self._field_props

    def get_format(self) -> str:
        if 'format' in self.field_props:
            return self._field_props['format']
        if 'enum' in self.field_props:
            return 'enum'
        return self._field_type

    def get_enum_values(self):
        if 'enum' in self.field_props:
            return self._field_props['enum']
        return None

    def __str__(self):
        return ('field_name：{},field_type:{},field_required:{},field_nullable:{},field_desc:{}'.
                format(self.field_name, self.field_type, self.field_required,
                       self.field_nullable, self.field_desc))


class StringField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(StringField, self).__init__(field_name, 'string', field_required, field_props)
        self.max_length = field_props.get('maxLength', None)


class IntegerField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(IntegerField, self).__init__(field_name, 'integer', field_required, field_props)
        self.minimum = field_props.get('minimum', None)
        self.maximum = field_props.get('maximum', None)


class NumberField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(NumberField, self).__init__(field_name, 'number', field_required, field_props)
        self.minimum = field_props.get('minimum', None)
        self.maximum = field_props.get('maximum', None)


class BooleanField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(BooleanField, self).__init__(field_name, 'boolean', field_required, field_props)


class ObjectField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(ObjectField, self).__init__(field_name, 'object', field_required, field_props)


class ArrayField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(ArrayField, self).__init__(field_name, 'array', field_required, field_props)
        """
        {'description': '库容变化', 'items': {'$ref': '#/components/schemas/MonitorRsvrDownwaterCapacity'}, 'type': 'array'}
        """
        if 'type' in field_props['items']:
            self.inner_type = field_props['items']['type']
        elif '$ref' in field_props['items']:
            parts = field_props['items']['$ref'].split('/')
            schema_name = parts[-1] if parts[-1] else None
            self.inner_type = schema_name

    def __str__(self):
        s = super(ArrayField, self).__str__()
        return f'{s},inner_type={self.inner_type}'


class UnknownField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(UnknownField, self).__init__(field_name, 'unknownfield', field_required, field_props)


class RefField(FieldBase):
    def __init__(self, field_name, field_required, field_props):
        super(RefField, self).__init__(field_name, 'ref', field_required, field_props)

        if '$ref' in field_props:
            parts = field_props['$ref'].split('/')
        elif 'allOf' in field_props:
            parts = field_props['allOf'][0]['$ref'].split('/')
        else:
            parts = []
            
        schema_name = parts[-1] if parts[-1] else None
        self.inner_type = schema_name

    def __str__(self):
        s = super(RefField, self).__str__()
        return f'{s},inner_type={self.inner_type}'
