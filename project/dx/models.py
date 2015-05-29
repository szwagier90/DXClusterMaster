from django.db import models
from django.contrib.auth.models import User

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

class Operator(models.Model):
    user = models.OneToOneField(User)
    callsign = models.CharField(max_length=20)
    locator = models.CharField(max_length=10)

    def __unicode__(self):
        ret = ""
        if self.callsign:
            ret += self.callsign
        else:
            ret += "callsign undefined"

        ret += ' | '

        if self.locator:
            ret += self.locator
        else:
            ret += "locator undefined"

        ret += ' | '

        ret += "User: "
        ret += self.user.username
        return ret
