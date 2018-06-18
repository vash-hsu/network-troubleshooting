#!/usr/bin/env python

import sqlite3
from Logger import Logger


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class DataBaseHelper(Singleton):
    path = None
    conn = None
    cursor = None

    def setup(self, path_db_file):
        self.path = path_db_file
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def createTable(self, table_name, sql_statement=None):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND " + \
              "name='%s';" % table_name
        self.cursor.execute(sql)
        # if table not found
        if len(self.cursor.fetchall()) == 0:
            if sql_statement:
                Logger.debug(sql_statement)
                self.cursor.execute(sql_statement)
                self.conn.commit()
                return True
            else:
                return False
        return True

    def sql(self, sql_statement):
        self.cursor.execute(sql_statement)
        return self.cursor.fetchall()

    def insert(self, table_name, data_set):
        length = len(data_set)
        sql_command = "INSERT into " + table_name + \
                      " VALUES (?" + " ,?" * (length-1) + ")"
        sql_param = data_set
        try:
            Logger.debug(sql_command)
            Logger.debug( repr(sql_param) )
            self.conn.execute(sql_command, sql_param)
            self.conn.commit()
        except Exception as err:
            Logger.error(err.message)
            Logger.error(repr(err))
