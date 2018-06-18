#!/usr/bin/env python


class Logger:
    def __init__(self):
        pass

    @classmethod
    def debug(cls, message):
        print("DEBUG: %s" % message)

    @classmethod
    def error(cls, message):
        print("ERROR: %s" % message)
