from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, StationFacility
# 编写自定义命令并运行

class Command(BaseCommand):
    help = 'Update the station name from "西朗" to "西塱"'

    def handle(self, *args, **options):
        old_name = "西朗"
        new_name = "西塱"

        try:
            station = Station.objects.get(station_name=old_name)
            station.station_name = new_name
            station.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated station name from "{old_name}" to "{new_name}"'))
        except Station.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Station with name "{old_name}" does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to update station name: {e}'))