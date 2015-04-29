from django.db import models

class Spot(models.Model):
    spotter = models.CharField(max_length=10)
    station = models.CharField(max_length=10)
    frequency = models.FloatField()
    comment = models.CharField(max_length=40)
    time = models.DateTimeField()
    locator = models.CharField(max_length=10)

    def __unicode__(self):
        ret = "DX de "
        ret += (self.spotter+":").ljust(7, ' ') + ' '
        ret += str(self.frequency).rjust(10, ' ') + '  '
        ret += self.station.ljust(13, ' ')
        ret += self.comment + " "
        ret += str(self.time.strftime('%H%M')) + "Z "
        ret += self.locator + " "
        return ret
