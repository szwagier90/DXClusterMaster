from django.core.management.base import BaseCommand
from dx.models import Spot

from DXClusterReader import DXClusterReader
from UsernameError import UsernameError

import time 

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            d = DXClusterReader()
            while True:
                spot = d.get_next_spot()
                self.stdout.write(spot)
        except UsernameError:
            self.stdout.write("Login Error - Bad Username")
        except KeyboardInterrupt:
            self.stdout.write("Ending program!!!")
        finally:
            self.stdout.write("Disconnecting 1...")
            d.disconnect()
