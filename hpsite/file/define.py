from enum import Enum


class FileAttr(Enum):
    LAST_MODIFY = 'lastModified'
    SIZE = 'size'
    NAME = 'fileName'


class OrderDirection(Enum):
    DESCENDING = 'Descending'
    ASCENDING = 'Ascending'


def check_parameter_follow_defined(param: str, define_cls: type(Enum)):
    define_param_list = [e.value for e in define_cls]

    return param in define_param_list




