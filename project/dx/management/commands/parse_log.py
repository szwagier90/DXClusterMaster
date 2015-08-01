from django.core.management.base import BaseCommand

from AdiLogParser import AdiLogParser

from dx.models import Operator, Band, Prefix, QSO, FileProcessingProgress

from django.db import IntegrityError
from drafts import colors

class LogEntryError(Exception):
    pass

class Command(BaseCommand):
    def handle(self, *args, **options):
        adi = AdiLogParser(args[0])
        try:
            operator = Operator.objects.get(user__username=args[1])

            fpp = FileProcessingProgress.objects.create(
                operator=operator,
                goal=len(adi.parsed_records),
            )

            for progress, record in enumerate(adi.parsed_records):
                fpp.progress = progress
                fpp.save()

                try:
                    prefix = self.get_or_create_prefix(record)

                    call = self.read_key_from_record('CALL', record)
                    date = self.read_key_from_record('DATE', record)

                    band = self.get_or_create_band(record)

                    frequency = self.read_key_from_record('FREQ', record)
                    locator = self.read_key_from_record('GRIDSQUARE', record)
                    mode = self.read_key_from_record('MODE', record)
                    rst_sent = self.read_key_from_record('RST_SENT', record)
                    rst_received = self.read_key_from_record('RST_RCVD', record)
                    qsl_confirmed = self.read_key_from_record('QSL_RCVD', record)
                    eqsl_confirmed = self.read_key_from_record('eQSL_QSL_RCVD', record)
                    lotw_confirmed = self.read_key_from_record('LOTW_QSL_RCVD', record)

                    qso, created = QSO.objects.get_or_create(
                        call=call,
                        date=date,
                        band=band,
                        frequency=frequency,
                        locator=locator,
                        mode=mode,
                        defaults={
                            'operator': operator,
                            'prefix': prefix,
                            'rst_sent': rst_sent,
                            'rst_received': rst_received,
                            'qsl_confirmed': qsl_confirmed,
                            'eqsl_confirmed': eqsl_confirmed,
                            'lotw_confirmed': lotw_confirmed,
                        }
                    )

                    if not created:
                        qso.qsl_confirmed = qsl_confirmed
                        qso.eqsl_confirmed = eqsl_confirmed
                        qso.lotw_confirmed = lotw_confirmed
                        qso.save()

                except IntegrityError:
                    print "IntegrityError"
                    continue
                except LogEntryError:
                    print colors.magenta("LogEntryError!")
                    print colors.cyan(record)

        except Operator.DoesNotExist:
            print "User %s does not have an Operator's account" % args[1]
        finally:
            fpp.delete()
            fpp = FileProcessingProgress.objects.filter(operator=operator).delete()

    def get_or_create_prefix(self, record):
        prefix = None

        callsign = self.read_key_from_record('CALL', record)
        try:
            prefix = Prefix.objects.get(full_callsign=True, name=callsign)
        except Prefix.DoesNotExist:
            prefix = self.match_prefix(record)
        return prefix

    def get_or_create_band(self, record):
        band_name = self.read_key_from_record('BAND', record)
        band, created = Band.objects.get_or_create(name=band_name)
        return band

    def match_prefix(self, record):
        prefix = None

        pfx = self.read_key_from_record('PFX', record)

        for i in range(len(pfx)):
            try:
                prefix = Prefix.objects.get(name=pfx[:len(pfx)-i])
            except Prefix.DoesNotExist:
                continue
            else:
                break
        else:
            prefix = self.create_prefix(record)
        return prefix

    def create_prefix(self, record):
        dxcc = self.read_key_from_record('DXCC', record)
        name = self.read_key_from_record('COUNTRY', record)
        entity, created = Entity.objects.get_or_create(
            id=dxcc,
            defaults={
                'id': dxcc, 
                'name': name
            }
        )

        pfx = self.read_key_from_record('PFX', record)
        cqz = self.read_key_from_record('CQZ', record)
        ituz = self.read_key_from_record('ITUZ', record)
        prefix = Prefix.objects.create(
            entity=entity,
            name=pfx,
            ituz=ituz,
            cqz=cqz,
            full_callsign=False
        )

        return prefix

    def read_key_from_record(self, key, record):
        exception_values = {
            'CALL': None,
            'DATE': None,
            'COUNTRY': None,
            'CQZ': None,
            'BAND': None,
            'ITUZ': None,
            'FREQ': None,
            'GRIDSQUARE': None,
            'MODE': None,
            'RST_SENT': None,
            'RST_RCVD': None,
            'QSL_RCVD': False,
            'eQSL_QSL_RCVD': False,
            'LOTW_QSL_RCVD': False,
        }

        try:
            return record[key]
        except KeyError:
            try:
                return exception_values[key]
            except KeyError:
                raise LogEntryError
