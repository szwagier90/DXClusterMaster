#!/usr/bin/env python

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from dx.models import Entity, Prefix
from django.db.utils import IntegrityError

import re

from drafts import colors


class MatchNotFound(Exception):
    pass

class StrangePrefix(Exception):
    pass

with open(r'drafts/cty.dat', 'r') as f:

    records = f.read().split(';\r\n')

    for one_record in records:
        try:
            all_lines = one_record.splitlines()

            first_line = all_lines[0]
            next_lines = all_lines[1:]

            country_name_string = first_line[:26]
            country_name = country_name_string[:country_name_string.index(':')]

            cq_zone_string = first_line[26:31]
            cqz = int(cq_zone_string[:cq_zone_string.index(':')])

            itu_zone_string = first_line[31:36]
            ituz = int(itu_zone_string[:itu_zone_string.index(':')])

            # continent_string = first_line[36:41]
            # continent = continent_string[:continent_string.index(':')]

            # latitude_string = first_line[41:50]
            # latitude = latitude_string[:latitude_string.index(':')]

            # longitude_string = first_line[50:60]
            # longitude = longitude_string[:longitude_string.index(':')]

            # time_offset_string = first_line[60:69]
            # time_offset = time_offset_string[:time_offset_string.index(':')]

            primary_dxcc_prefix_string = first_line[69:75]
            try:
                primary_dxcc_prefix = primary_dxcc_prefix_string[:primary_dxcc_prefix_string.index(':')]
            except ValueError:
                print "VALUE ERROR PRIMARY DXCC PREFIX"
                print colors.green(first_line)
                print colors.blue(primary_dxcc_prefix_string)

            # print colors.green("Country Name: %s" % country_name)
            # print colors.green("CQ Zone: %s" % cqz)
            # print colors.green("ITU Zone: %s" % ituz)
            # print colors.green("Continent: %s" % continent)
            # print colors.green("Latitude: %s" % latitude)
            # print colors.green("Longitude: %s" % longitude)
            # print colors.green("Time offset: %s" % time_offset)
            # print colors.green("Primary DXCC prefix: %s" % primary_dxcc_prefix)

            prefixes = []
            for l in all_lines[1:]:
                prefixes.extend(l.split(','))
            prefixes = filter(None, prefixes)
            prefixes = map(str.strip, prefixes)

            try:
                entity = Entity.objects.get(name=country_name)
            except Entity.MultipleObjectsReturned:
                print country_name
                raise Entity.MultipleObjectsReturned
            except Entity.DoesNotExist:
                print colors.yellow('DoesNotExist!')
                cut = 0
                entity = None
                while not entity:
                    cut += 1
                    if cut == len(country_name):
                        raise MatchNotFound
                    
                    country_filter = country_name[:-cut]

                    found_entities = Entity.objects.filter(name__startswith=country_filter)
                    if not found_entities:
                        continue

                    print "To match: %s" % colors.magenta(country_name)
                    print "country_filter: %s" % colors.green(country_filter)

                    confirmation = 'n'
                    while confirmation not in ['', 'y', 'Y']:
                        for i, e in enumerate(found_entities):
                            print "[%d] - %s" % (i, e.name)
                        
                        choice = raw_input("Choose any option or hit enter: ")
                        if not choice:
                            break

                        entity = found_entities[int(choice)]
                        confirmation = raw_input("Really %s? [Y]: " % colors.yellow(entity.name))
                        if confirmation in ['', 'y', 'Y']:
                            decision = raw_input("Do you want to overwrite old name %s with new name %s [Y]? " % (colors.magenta(entity.name), colors.green(country_name)))
                            if decision in ['', 'y', 'Y']:
                                entity.name = country_name
                                entity.save()

            for p in prefixes:
                try:
                    grouped_prefix = re.match(r'^(?P<full_callsign>=)?(?P<name>[A-Z0-9/]+)(\((?P<cqz>\d+)\))?(\[(?P<ituz>\d+)\])?$', p)
                    if not grouped_prefix:
                        print colors.green(p)
                        raise StrangePrefix
                    if grouped_prefix.group('full_callsign'):
                        full_callsign = True
                    else:
                        full_callsign = False

                    prefix = Prefix.objects.create(
                        entity=entity,
                        name = grouped_prefix.group('name'),
                        ituz = int(grouped_prefix.group('ituz') or ituz),
                        cqz = int(grouped_prefix.group('cqz') or cqz),
                        full_callsign = full_callsign)
                except IntegrityError:
                    print colors.cyan(p),
                    print colors.red("already EXISTS in database!")
                    continue
        except MatchNotFound:
            print colors.cyan(one_record) + colors.red(" has no matching Entity!")
