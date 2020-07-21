
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from respa_berth.models.berth import Berth


class Command(BaseCommand):
    help = 'Seek for duplicate berths.'

    def handle(self, *args, **options):
        berths = Berth.objects.all()

        for berth in berths:
            resource = berth.resource
            unit = berth.resource.unit
            seek = Berth.objects.filter(resource__name=resource.name, resource__unit__name=unit.name)
            if len(seek) > 1:
                lookup = '[unit_name: {}, resource_name: {}, resource_id: {}]'.format(unit.name, resource.name, resource.id)
                print(lookup)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
