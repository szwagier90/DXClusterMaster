#!/usr/bin/env python

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
        return parsed_record