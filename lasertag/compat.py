import sys

IS_PYTHON_3 = sys.version_info >= (3, 0)

if IS_PYTHON_3:
    STRING_TYPES = (str, )
else:
    STRING_TYPES = (str, unicode)


def is_string(v):
    return isinstance(v, STRING_TYPES)
