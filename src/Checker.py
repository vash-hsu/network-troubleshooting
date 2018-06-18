#!/usr/bin/env python


class Checker:
    def __init__(self):
        pass

    @classmethod
    def contain_illegal_char(cls, string):
        try:
            utf8_version = string.encode('ascii')
        except UnicodeDecodeError:
            return True
        if len(utf8_version) > 255:
            return True
        return False