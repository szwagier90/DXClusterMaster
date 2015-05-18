#!/usr/bin/env python

import unittest
from AdiLogParser import AdiLogParser
from datetime import datetime
import pytz

test_record1 = '<BAND:3>80M <CALL:6>SP3CMX <CONT:2>EU <CQZ:2>15 <DXCC:3>269 <ITUZ:2>28 <MODE:3>SSB <OPERATOR:6>SP6QNU <PFX:3>SP3 <APP_LOGGER32_QSL:1>Y <QSL_SENT:1>Y <QSLMSG:11>73 - Mietek <QSO_DATE:8:D>20090915 <TIME_ON:6>165400 <RST_SENT:2>59 <TIME_OFF:6>165400 <eQSL_QSL_SENT:1>Y <LOTW_QSL_SENT:1>Y <APP_LOGGER32_QSO_NUMBER:1>3 <COUNTRY:6>Poland <APP_LOGGER32_LAT:5>52.39 <APP_LOGGER32_LNG:6>-16.84 <EOR>'

class ADItesting(unittest.TestCase):
    def setUp(self):
        self.parser = AdiLogParser("test_log.adi")

    def test_class_constructor(self):
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.path, "test_log.adi")

    def test_get_one_record(self):
        self.assertEqual(self.parser.records[2], test_record1)

    def test_parse_first_record(self):
        parsed_record = self.parser.parse_one_record(test_record1)
        self.assertIsInstance(parsed_record, dict)
        self.assertTrue("BAND" in parsed_record.keys())
        self.assertEqual(parsed_record["BAND"], "80M")
        self.assertEqual(parsed_record["CALL"], "SP3CMX")
        self.assertEqual(parsed_record["CONT"], "EU")
        self.assertEqual(parsed_record["CQZ"], 15)
        self.assertEqual(parsed_record["DXCC"], 269)
        self.assertEqual(parsed_record["ITUZ"], 28)
        self.assertEqual(parsed_record["MODE"], "SSB")
        self.assertEqual(parsed_record["OPERATOR"], "SP6QNU")
        self.assertEqual(parsed_record["PFX"], "SP3")
        self.assertEqual(parsed_record["APP_LOGGER32_QSL"], True)
        self.assertEqual(parsed_record["QSL_SENT"], True)
        self.assertEqual(parsed_record["QSLMSG"], "73 - Mietek")
        self.assertEqual(parsed_record["QSO_DATE"], "20090915")
        self.assertEqual(parsed_record["TIME_ON"], "165400")
        self.assertEqual(parsed_record["RST_SENT"], "59")
        self.assertEqual(parsed_record["TIME_OFF"], "165400")
        self.assertEqual(parsed_record["eQSL_QSL_SENT"], True)
        self.assertEqual(parsed_record["LOTW_QSL_SENT"], True)
        self.assertEqual(parsed_record["APP_LOGGER32_QSO_NUMBER"], 3)
        self.assertEqual(parsed_record["COUNTRY"], "Poland")
        self.assertEqual(parsed_record["APP_LOGGER32_LAT"], 52.39)
        self.assertEqual(parsed_record["APP_LOGGER32_LNG"], -16.84)
        self.assertEqual(parsed_record["DATE"], datetime(2009, 9, 15, 16, 54, 0, tzinfo=pytz.utc))

if __name__ == '__main__':
    unittest.main()