#!/usr/bin/env python

from DataBaseHelper import DataBaseHelper


class CacheManager:

    def __init__(self, name_table, path_database=None):
        self.database = DataBaseHelper()
        self.table_name = name_table
        if path_database:
            self.database.setup(path_database)
        else:
            self.database.setup("db.sqlite")

    def setup(self, sql_table_creation):
        self.database.createTable(self.table_name,
                                  sql_statement=sql_table_creation)

    def retrieve_from_cache(self, field_name, field_value):
        sql = "SELECT * FROM %s WHERE %s='%s';" %\
              (self.table_name, field_name, field_value)
        results = self.database.sql(sql)
        if len(results) > 0:
            return results[0]
        else:
            return None

    def insert_to_cache(self, list_paris):
        self.database.insert(self.table_name, list_paris)
