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

class Entity(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField('DXCC name', max_length=50)

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    def __unicode__(self):
        return "%d: %s" % (self.id, self.name)

class Prefix(models.Model):
    entity = models.ForeignKey(Entity)
    name = models.CharField('Prefix', primary_key=True, max_length=20)
    ituz = models.PositiveSmallIntegerField('ITU Zone')
    cqz = models.PositiveSmallIntegerField('CQ Zone')
    full_callsign = models.BooleanField('Full callsign', default=False)

    class Meta:
        verbose_name = "Prefix"
        verbose_name_plural = "Prefixes"

    def __unicode__(self):
        return "Prefix %s (%s): ITU:%d CQ: %d [Full: %s]" % (
            self.name,
            self.entity.name,
            self.ituz,
            self.cqz,
            str(self.full_callsign),
        )

class QSO(models.Model):
    operator = models.ForeignKey(Operator)
    call = models.CharField(max_length=20)

    prefix = models.ForeignKey(Prefix)

    date = models.DateTimeField(null=True)
    band = models.CharField(max_length=6)
    frequency = models.FloatField('Frequency [MHz]', null=True)
    locator = models.CharField(max_length=10, null=True)
    mode = models.CharField(max_length=5, null=True)
    rst_sent = models.CharField('RST Sent', max_length=3, null=True)
    rst_received = models.CharField('RST Received', max_length=3, null=True)

    qsl_confirmed = models.BooleanField('QSL Confirmation', default=False)
    eqsl_confirmed = models.BooleanField('eQSL Confirmation', default=False)
    lotw_confirmed = models.BooleanField('LOTW Confirmation', default=False)

    class Meta:
        verbose_name = "QSO"
        verbose_name_plural = "QSOs"

    def __unicode__(self):
        ret = ""

        ret += self.operator.callsign.upper()
        ret += ' -> '
        ret += self.call

        ret += ' | '

        if self.date:
            ret += str(self.date)
        else:
            ret += "date undefined"

        ret += ' | '

        if self.is_confirmed():
            ret += "CONFIRMED"
        else:
            ret += "NOT CONFIRMED"

        return ret

    def is_confirmed(self):
        return self.qsl_confirmed or self.eqsl_confirmed or self.lotw_confirmed
