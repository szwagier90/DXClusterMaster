#!/usr/bin/env python

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from dx.models import Entity

import re
from django.db.utils import IntegrityError

from drafts import colors

with open(r'drafts/country_list.txt', 'r') as f:

    lines = f.read().splitlines()

    for line in lines:
        columns = re.split('\s{2,}', line)
        name = columns[1]
        dxcc = int(columns[5])

        print "%s %s" % (colors.yellow("Name: "), colors.green(name))
        print "%s %s" % (colors.yellow("DXCC: "), colors.green(dxcc))

        try:
            e = Entity.objects.create(id=dxcc, name=name)
            print colors.green("CREATED!")
        except IntegrityError:
            e = Entity.objects.get(id=dxcc)
            print colors.magenta("NOT CREATED!")

            decision = raw_input("Correct entry for id=%d - '%s'? " % (e.id, e.name))
            if decision in ['', 'y', 'Y']:
                continue
            else:
                use_name_from_file = raw_input("Do you want to use name for id=%d from the file? Name from file: %s " % (e.id, name))
                if use_name_from_file in ['', 'y', 'Y']:
                    e.name = name
                else:
                    correct_name = raw_input("Type correct name for id=%d: " % e.id)
                    e.name = correct_name
                e.save()
