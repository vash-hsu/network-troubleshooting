#!/usr/bin/env python

import xlsxwriter


class XlsxHelper:

    def __init__(self, filename):
        self.workbook = xlsxwriter.Workbook(filename)
        pass

    def __delete__(self, instance):
        self.workbook.close()

    def read(self):
        pass

    def write(self, label_name, header, body_iterator):
        worksheet = self.workbook.add_worksheet(label_name)
        worksheet.write_row('A1', header)
        offset = 2
        for line in body_iterator:
            print line
            worksheet.write_row("A%d" % offset, line)
            offset += 1
