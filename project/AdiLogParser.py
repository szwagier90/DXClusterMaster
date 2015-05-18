#!/usr/bin/env python

import re

class AdiLogParser:
    def __init__(self, path):
        self.path = path
        self.records = None
        self.is_valid = False

        self.get_useful_records()

    def get_useful_records(self):
        with open(self.path) as adi_file:
            while True:
                line = adi_file.readline()
                if line == "\r\n":
                    break

            raw = adi_file.read().splitlines()
            self.records = [line for line in raw if line]

    def parse_one_record(self, record):
        parsed_record = dict()
        replaced_record = record.replace('>>', '$3e3e').replace('<<', '$3c3c')
        tags = re.findall('<(.*?):(\d+).*?>([^<\t\n\r\f\v]+ )', replaced_record)
        for t in tags:
            key = t[0]
            corrected_value = t[2].replace('$3e3e', '>>').replace('$3c3c', '<<')
            value = corrected_value[:int(t[1])]

            if key == 'CQZ':
                value = int(value)
            elif key == 'DXCC':
                value = int(value)
            elif key == 'ITUZ':
                value = int(value)
            elif key == 'APP_LOGGER32_QSL':
                value = self.ascii_to_bool(value)
            elif key == 'QSL_SENT':
                value = self.ascii_to_bool(value)
            elif key == 'APP_LOGGER32_QSL':
                value = self.ascii_to_bool(value)
            elif key == 'eQSL_QSL_SENT':
                value = self.ascii_to_bool(value)
            elif key == 'LOTW_QSL_SENT':
                value = self.ascii_to_bool(value)
            elif key == "APP_LOGGER32_QSO_NUMBER":
                value = int(value)
            elif key == "APP_LOGGER32_LAT":
                value = float(value)
            elif key == "APP_LOGGER32_LNG":
                value = float(value)

            parsed_record[key] = value

        parsed_record['DATE'] = None
        return parsed_record

    def ascii_to_bool(self, value):
        if value == 'Y':
            return True
        elif value == 'N':
            return False
