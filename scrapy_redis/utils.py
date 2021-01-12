# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     utils
   Description :
   Author :       dean
   date：          2020/7/20 14:04
-------------------------------------------------
   Change Activity:
                   14:04
-------------------------------------------------
"""

import six


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if six.PY3 and isinstance(s, bytes):
        return s.decode(encoding)
    return s