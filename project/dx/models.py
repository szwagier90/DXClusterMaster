from django.db import models

class Spot(models.Model):
    spotter = models.CharField(max_length=10)
    station = models.CharField(max_length=10)
    frequency = models.FloatField()
    comment = models.CharField(max_length=40)
    time = models.DateTimeField()
    locator = models.CharField(max_length=10)

    def __unicode__():
        ret = ""
        ret += spotter + " "
        ret += station + " "
        ret += frequency + " "
        ret += comment + " "
        ret += time + " "
        ret += locator + " "
        return ret
