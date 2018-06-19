#!/usr/bin/env python

from NetworkUtil import HttpInfo
from CacheManager import CacheManager
from Logger import Logger
from XlsxUtil import XlsxHelper

import os
import sys
import getopt
from datetime import datetime


def usage(script_name):
    print"""\
Usage: python %s -r <File listing Url> [-w <XLSX Report>] [-d <DB file>]
       python %s <Hostname>
       -r  url in plaintext, line by line
       -w  default is YYYY-MMDD-HHMMSS.xlsx
       -d  database file, default is db.sqlite
ex.  : python %s https://www.google.com
ex.  : python %s -r urls.txt -w report.xlsx
ex.  : python %s -r urls.txt -w report.xlsx -d db.sqlite
""" % (script_name, script_name, script_name, script_name, script_name)


def candidate_filename():
    return datetime.now().strftime("%Y-%m%d-%H%M%S")


def parse_parameters(params, config):
    """
    config = dict()
    config[read]  :  url list file
    config[write] :  xlsx to write
    config[db]    :  database for caching query
    """
    file2read = None
    file2write = None
    db4cache = None
    hostnames = list()
    if len(params) == 0:
        return False
    try:
        opts, args = getopt.getopt(params,
                                   "hr:w:d:",
                                   ['help', ])
    except getopt.GetoptError as err:
        Logger.error(err.msg)
        return False
    for opt, arg in opts:
        if opt in ['-r']:
            if os.path.exists(arg) and os.path.isfile(arg):
                file2read = os.path.realpath(arg)
            else:
                Logger.error("invalid file path to read: " + arg)
                return False
        elif opt in ['-w']:
            if os.path.exists(arg) and os.path.isdir(arg):
                file2write = os.path.join(arg, candidate_filename() + '.xlsx')
            else:
                file2write = arg
        elif opt in ['-d']:
            if os.path.isfile(arg):
                db4cache = arg
            elif os.path.exists(arg) and os.path.isdir(arg):
                db4cache = os.path.join([arg, 'db.sqlite'])
    for argv in args:
        hostnames.append(argv)
    # at least one in hostnames or file2read
    if len(hostnames) == 0 and not file2read:
        return False
    if file2read:
        config['read'] = file2read
    if file2write:
        config['write'] = file2write
    if db4cache:
        config['db'] = db4cache
    if len(hostnames):
        config['url'] = hostnames
    return True


class AnswerHttpPing_withCache:

    def __init__(self, path_db = None):
        self.httping = HttpInfo()
        table_name = "httping"
        if path_db:
            self.cache = CacheManager(name_table=table_name,
                                      path_database=path_db)
        else:
            self.cache = CacheManager(name_table=table_name,
                                      path_database=os.path.join(
                                          os.getcwd(), "db.sqlite"))
        self.cache.setup("CREATE TABLE %s ("
                         "_url TEXT PRIMARY KEY, "
                         "code TEXT, "
                         "size TEXT, "
                         "duration TEXT);" % table_name)

    def query(self, url):
        from_cache = self.cache.retrieve_from_cache("_url", url)
        if from_cache:
            Logger.debug("from cache for %s" % url)
            return from_cache
        else:
            from_query = self.httping.query(url)
            Logger.debug("from query for %s" % url)
            if from_query:
                terms = [from_query['url'], str(from_query['code']),
                         str(from_query['size']), str(from_query['duration'])]
                self.cache.insert_to_cache(terms)
                return terms


def batch_query(file2read, file2write, query_helper):
    writer = XlsxHelper(file2write)
    header = ['url', 'code', 'size', 'duration']

    def body():
        with open(file2read, 'rt') as reader:
            for line in reader:
                question = line.rstrip()
                answer = query_helper.query(question)
                yield list(answer)

    writer.write('httping', header, body())


def test():
    questions = ["https://www.google.com", "https://www.facebook.com",
                 "https://www.cnn.com", "https://www.yahoo.com"]
    answer = HttpInfo()
    for i in questions:
        print answer.query(i)
        print answer.code, answer.size, answer.KB_ps, answer.MB_ps


if __name__ == '__main__':
    config = dict()
    if not parse_parameters(sys.argv[1:], config):
        usage(os.path.split(sys.argv[0])[-1])
        exit(0)
    if 'db' in config:
        finder = AnswerHttpPing_withCache(config['db'])
    else:
        finder = AnswerHttpPing_withCache()
    # stdout only
    if 'url' in config:
        for i in config['url']:
            print ", ".join(finder.query(i))
    # file in, file out
    if 'read' in config:
        if 'write' in config:
            report = config['write']
        else:
            report = candidate_filename() + ".xlsx"
        batch_query(config['read'], report, finder)
