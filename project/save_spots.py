#!/usr/bin/env python

import time 
import sys

time.sleep(1)

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from dx.models import Spot

from DXClusterReader import DXClusterReader
from UsernameError import UsernameError
import spot

try:
    while True:
        new_spot = None
        try:
            d = DXClusterReader()
            while True:
                new_spot = d.get_next_spot()
                s = spot.Spot(new_spot)
                print s

                spot_object = Spot()
                spot_object.spotter = s.spotter_call
                spot_object.station = s.dx_call
                spot_object.frequency = s.frequency
                spot_object.comment = s.comment
                spot_object.time = s.time
                spot_object.locator = s.locator
                spot_object.save()
                
        except UsernameError:
            print >> sys.stderr, "Login Error - Bad Username"
        except TypeError:
            print new_spot
        finally:
            print >> sys.stderr, "Disconnecting 1..."
            d.disconnect()
except KeyboardInterrupt:
    print >> sys.stderr, "KeyboardInterrupt!!!"
