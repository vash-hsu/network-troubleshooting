#!/usr/bin/env python

from NetworkUtil import IPInfo
from CacheManager import CacheManager
from Logger import Logger
from XlsxUtil import XlsxHelper

import os
import sys
import getopt
from datetime import datetime


def usage(script_name):
    print"""\
Usage: python %s -r <File listing Hostname> [-w <XLSX Report>] [-d <DB file>]
       python %s <Hostname>
       -r  hostname in plaintext, line by line
       -w  default is YYYY-MMDD-HHMMSS.xlsx
       -d  database file, default is db.sqlite
ex.  : python %s google.com
ex.  : python %s -r hosts.txt -w report.xlsx
ex.  : python %s -r hosts.txt -w report.xlsx -d db.sqlite
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
        config['hostname'] = hostnames
    return True


class AnswerIPInfo_withCache:

    def __init__(self, path_db = None):
        self.ipinfo = IPInfo()
        if path_db:
            self.cache = CacheManager(name_table="ipinfo",
                                      path_database=path_db)
        else:
            self.cache = CacheManager(name_table="ipinfo",
                                      path_database=os.path.join(
                                          os.getcwd(), "db.sqlite"))
        self.cache.setup("CREATE TABLE %s ("
                         "_hostname TEXT PRIMARY KEY, "
                         "city TEXT, "
                         "country TEXT, "
                         "countryCode TEXT, "
                         "org TEXT, "
                         "query TEXT);" % "ipinfo")

    def query(self, hostname):
        from_cache = self.cache.retrieve_from_cache("_hostname", hostname)
        if from_cache:
            Logger.debug("from cache for %s" % hostname)
            return from_cache
        else:
            from_query = self.ipinfo.query(hostname)
            Logger.debug("from query for %s" % hostname)
            if from_query:
                self.cache.insert_to_cache(
                    [from_query['hostname'], from_query['city'],
                     from_query['country'], from_query['countryCode'],
                     from_query['org'], from_query['query']])
                return from_query


def batch_query(file2read, file2write, query_helper):
    writer = XlsxHelper(file2write)
    header = ['hostname', 'city', 'country', 'countryCode', 'org', 'query']

    def body():
        with open(file2read, 'rt') as reader:
            for line in reader:
                question = line.rstrip()
                answer = query_helper.query(question)
                yield list(answer)

    writer.write('ipinfo', header, body())


def test():
    questions = [u"www.google.com", u"www.facebook.com", u"www.cnn.com",
                 u"www.yahoo.com"]
    answer = AnswerIPInfo_withCache()
    for i in questions:
        print answer.query(i)


if __name__ == '__main__':

    config = dict()
    if not parse_parameters(sys.argv[1:], config):
        usage(os.path.split(sys.argv[0])[-1])
        exit(0)
    if 'db' in config:
        finder = AnswerIPInfo_withCache(config['db'])
    else:
        finder = AnswerIPInfo_withCache()
    # stdout only
    if 'hostname' in config:
        for i in config['hostname']:
            print ", ".join(finder.query(i))
    # file in, file out
    if 'read' in config:
        if 'write' in config:
            report = config['write']
        else:
            report = candidate_filename() + ".xlsx"
        batch_query(config['read'], report, finder)
