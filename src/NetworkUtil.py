#!/usr/bin/env python


from Logger import Logger
from urllib3 import Retry, Timeout, PoolManager
from urllib3 import exceptions as urllibs_exceptions
from Checker import Checker
from datetime import datetime
from time import sleep
import json


try:
    from json.decoder import JSONDecoderError
except ImportError:
    JSONDecoderError = ValueError


MAX_RETRY = 2
SEC_FOR_BACKOFF = 0.5 # sleep 0.5, 1.0, 2.0, 4.0, ... before next retry
SEC_BETWEEN_DYNAMIC_QUERY = 0.5


class IPInfo:

    def __init__(self):
        self.last = None # time-stamp of last query
        self.meta = None

    def setup(self):
        self.meta = {'hostname': '',
                     'city': '',
                     'country': '',
                     'countryCode': '',
                     'lat': '',
                     'lon': '',
                     'org': '',
                     'query': '',  # IP
                     }

    def query(self, hostname):
        self.setup()
        self.meta['hostname'] = hostname
        if Checker.contain_illegal_char(hostname):
            return self.meta
        else:
            self.query_ip_api(hostname, self.meta)
            Logger.debug("IPInfo.query() with %s" % hostname )
            Logger.debug(repr(self.meta))
            return self.meta

    def query_ip_api(self, hostname, dict_result):
        target_url = "http://ip-api.com/json/" + hostname
        retries = Retry(connect=MAX_RETRY,
                        read=MAX_RETRY,
                        status=MAX_RETRY,
                        redirect=2,
                        backoff_factor=SEC_FOR_BACKOFF)
        timeout = Timeout(connect=3.0, read=2.0)
        worker = PoolManager(retries=retries, timeout=timeout)

        try:
            # prevention of DOS
            if self.last:
                delta = datetime.now() - self.last
                delay_offset = delta.total_seconds()
                if delay_offset < SEC_BETWEEN_DYNAMIC_QUERY:
                    sec2sleep = SEC_BETWEEN_DYNAMIC_QUERY - delay_offset
                    Logger.debug("sleep %f seconds because of setting %f" %
                          (sec2sleep, SEC_BETWEEN_DYNAMIC_QUERY))
                    sleep(sec2sleep)
            # action
            request = worker.request('GET', target_url)
            if request.status == 200:
                page = json.loads(request.data)
                try:
                    for name in dict_result.keys():
                        if name in page:
                            dict_result[name] = page[name]
                    self.last = datetime.now()
                except KeyError:
                    Logger.error("Failed parse JSON from GET %s" % target_url)
                    Logger.error(request.data)
        except urllibs_exceptions as err:
            if 'message' in dir(err):
                Logger.error(err.message)
            else:
                Logger.error(err.__name__)
        except JSONDecoderError as err:
            if 'message' in dir(err):
                Logger.error(err.message)
            else:
                Logger.error(err.__name__)

