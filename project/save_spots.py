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

from datetime import datetime

from django.db.utils import OperationalError

while True:
    try:
        new_spot = None
        d = None
        try:
            print >> sys.stderr, "Connecting..."
            d = DXClusterReader(timeout=60)
            print >> sys.stderr, "Connected!"
            while True:
                print "Awaiting a new spot"
                new_spot = d.get_next_spot()
                print "Received a new spot!"
                s = spot.Spot(new_spot)
                print s

                spot_object = Spot()
                spot_object.spotter = s.spotter_call
                spot_object.station = s.dx_call
                spot_object.frequency = s.frequency
                spot_object.comment = s.comment
                spot_object.time = s.time
                spot_object.locator = s.locator

                save_attempt = 0
                while True:
                    save_attempt += 1
                    if save_attempt > 10:
                        raise OperationalError

                    try:
                        spot_object.save()
                    except OperationalError:
                        print >> sys.stderr, "OperationalError (wait %d seconds...): " % save_attempt,
                        time.sleep(save_attempt)
                    else:
                        break
                print "New spot has been SAVED!"
                
        except UsernameError:
            print >> sys.stderr, "Login Error - Bad Username"
        except TypeError:
            print >> sys.stderr, "TypeError (Probably an announcement): ",
        except BufferError:
            print >> sys.stderr, "BufferError (60s timeout): ",
        finally:
            print >> sys.stderr, datetime.now()
            d.disconnect()
    except AttributeError:
        print >> sys.stderr, "AttributeError (Cannot connect - 60s delay): ",
        for i in range(60):
            print '.',
            time.sleep(1)
