#!/usr/bin/env python

import unittest
from AdiLogParser import AdiLogParser

test_record = '<BAND:3>80M <CALL:6>SP3CMX <CONT:2>EU <CQZ:2>15 <DXCC:3>269 <ITUZ:2>28 <MODE:3>SSB <OPERATOR:6>SP6QNU <PFX:3>SP3 <APP_LOGGER32_QSL:1>Y <QSL_SENT:1>Y <QSLMSG:11>73 - Mietek <QSO_DATE:8:D>20090915 <TIME_ON:6>165400 <RST_SENT:2>59 <TIME_OFF:6>165400 <eQSL_QSL_SENT:1>Y <LOTW_QSL_SENT:1>Y <APP_LOGGER32_QSO_NUMBER:1>3 <COUNTRY:6>Poland <APP_LOGGER32_LAT:5>52.39 <APP_LOGGER32_LNG:6>-16.84 <EOR>'

class ADItesting(unittest.TestCase):
    def setUp(self):
        self.parser = AdiLogParser("test_log.adi")

    def test_class_constructor(self):
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.path, "test_log.adi")

    def test_get_one_record(self):
        self.assertEqual(self.parser.records[2], test_record)

    def test_parse_one_record(self):
        parsed_record = self.parser.parse_one_record(test_record)
        self.assertIsInstance(parsed_record, dict)

if __name__ == '__main__':
    unittest.main()