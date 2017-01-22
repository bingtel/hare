# -*- coding: utf-8 -*-


class Column(object):
    """column in table
    """

    def __init__(self, column_name=None, ordinal_position=None,
                 column_default=None, is_nullable=None, data_type=None,
                 character_maximum_length=None, character_octet_length=None,
                 column_key=None, extra=None):
        self.column_name = column_name
        self.ordinal_position = ordinal_position
        self.column_default = column_default
        self.is_nullable = is_nullable
        self.data_type = data_type
        self.character_maximum_length = character_maximum_length
        self.character_octet_length = character_octet_length
        self.column_key = column_key
        self.extra = extra
