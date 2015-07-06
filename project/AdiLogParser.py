#!/usr/bin/env python

import re
import datetime
import time
import pytz

class AdiLogParser:
    def __init__(self, path):
        self.path = path
        self.records = None
        self.parsed_records = []

        self.is_valid = False

        self.get_useful_records()
        self.parse_all_records()

    def get_useful_records(self):
        with open(self.path, 'r') as adi_file:
            #skip headline
            while True:
                line = adi_file.readline()
                if line == "\r\n":
                    break
            #--

            raw = adi_file.read().split('\r\n\r\n')
            self.records = [line for line in raw if line]

    def parse_all_records(self):
        for record in self.records:
            self.parsed_records.append(self.parse_one_record(record))

    def parse_one_record(self, record):
        parsed_record = dict()
        replaced_record = record.replace('>>', '$3e3e').replace('<<', '$3c3c')
        tags = re.findall('<(.*?):(\d+).*?>([^<\t\n\r\f\v]+ )', replaced_record)

        for t in tags:
            key = t[0]
            corrected_value = t[2].replace('$3e3e', '>>').replace('$3c3c', '<<')
            value = corrected_value[:int(t[1])]

            try:
                parsed_value = self.parse_value(key, value)
            except KeyError:
                continue
            except ValueError:
                continue
            else:
                parsed_record[key] = parsed_value

        try:
            parsed_record['DATE'] = datetime.datetime.combine(parsed_record['QSO_DATE'], parsed_record['TIME_ON']).replace(tzinfo=pytz.UTC)
        except KeyError:
            parsed_record['DATE'] = None

        return parsed_record

    def parse_value(self, key, value):
        function_dictionary = {
            'BAND': None,
            'CALL': None,
            'COUNTRY': None,
            'CQZ': int,
            'CREDIT_GRANTED': self.ascii_to_credits,
            'DXCC': int,
            'FREQ': float,
            'GRIDSQUARE': None,
            'ITUZ': int,
            'MODE': None,
            'PFX': None,
            'QSL_RCVD': self.ascii_to_bool,
            'QSO_DATE': self.ascii_to_date,
            'RST_RCVD': None,
            'RST_SENT': None,
            'TIME_ON': self.ascii_to_time,
            'eQSL_QSL_RCVD': self.ascii_to_bool,
            'LOTW_QSL_RCVD': self.ascii_to_bool,
        }

        function_to_call = function_dictionary[key]
        try:
            return function_to_call(value)
        except TypeError:
            return value

    def ascii_to_time(self, value):
        hour = int(value[0:2])
        minute = int(value[2:4])
        second = int(value[4:6])

        time = datetime.time(hour=hour, minute=minute, second=second)
        return time

    def ascii_to_date(self, value):
        year = int(value[0:4])
        month = int(value[4:6])
        day = int(value[6:8])

        date = datetime.date(year=year, month=month, day=day)
        return date

    def ascii_to_bool(self, value):
        if value == 'Y':
            return True
        elif value == 'N':
            return False

    def ascii_to_credits(self, value):
        credits = value.split(',')
        return credits

    def p(self, t):
        print "function not specified",
        return t
