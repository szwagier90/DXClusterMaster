import re
from datetime import datetime
import pytz

class Spot(object):
    def __init__(self, raw_spot):
        self.raw_spot = raw_spot
        self.valid = None
        self.dx_call = None
        self.spotter_call = None
        self.spotter_station = None
        self.frequency = None
        self.time = None
        self.comment = ""
        self.mode = None
        self.band = None
        self.locator = None

        if self.__process_spot(raw_spot):
        #   self.dx_station = Station(self.dx_call)
        #   self.spotter_station = Station(self.spotter_call)
        #   if self.dx_station.valid & self.spotter_station.valid:
            self.valid = True
        #   else:
        #       self.valid = False
        else: self.valid = False
    
    def __str__(self):
        ret = ""
        ret += "DX de "
        ret += self.spotter_call
        ret += ": "
        ret += str(self.frequency)
        ret += " "
        ret += self.dx_call
        ret += " "
        ret += self.comment
        ret += " "
        ret += str(self.time)
        ret += " "
        ret += self.locator
        return ret 

    def __process_spot(self, raw_string):
        try:
            spotter_call_temp = re.match('[A-Za-z0-9\/]+[:$]', raw_string[6:15])
            if spotter_call_temp:
                self.spotter_call = re.sub(':', '', spotter_call_temp.group(0))
            else:
                self.spotter_call = re.sub('[^A-Za-z0-9\/]+', '', raw_string[6:15])

            frequency_temp = re.search('[0-9\.]{5,12}', raw_string[10:25])
            if frequency_temp:
                self.frequency = float(frequency_temp.group(0))
            else:
                self.frequency = float(re.sub('[^0-9\.]+', '', raw_string[16:25]))
                raise Exception("Could not decode frequency")

            self.dx_call = re.sub('[^A-Za-z0-9\/]+', '', raw_string[26:38])
            self.comment = re.sub('[^\sA-Za-z0-9\.,;\#\+\-!\?\$\(\)@\/]+', ' ', raw_string[39:69])
            time_temp = re.sub('[^0-9]+', '', raw_string[70:74])
            self.time = datetime.utcnow().replace(hour=int(time_temp[0:2]), minute=int(time_temp[2:4]), second=0, microsecond = 0, tzinfo=pytz.utc)
            self.locator = re.sub('[^A-Za-z0-9]+', '', raw_string[75:80])
            return(True)
        except Exception as e:
            return(False)
