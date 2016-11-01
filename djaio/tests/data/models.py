from djaio.core.models import Model
from schematics import types


class TstInputDetail(Model):
    id = types.IntType(serialized_name='id', required=True)

class TstInput(Model):
    id = types.IntType(serialized_name='id', required=True)
    name = types.StringType(serialized_name='name')

class TstPostInput(Model):
    id = types.IntType(serialized_name='id', required=True)
    name = types.StringType(serialized_name='name', required=True)


class TstOutput(Model):
    id = types.IntType(serialized_name='id', required=True)
    name = types.StringType(serialized_name='name', required=True)
    guid = types.UUIDType(serialized_name='guid', required=True)
