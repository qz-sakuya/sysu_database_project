from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, \
    StationFacility, Image


'''
自动计算换乘数据并添加

python manage.py auto_add_transfer
'''



class Command(BaseCommand):
    help = 'Create transfer data for platforms within the same station'

    def handle(self, *args, **kwargs):
        stations = Station.objects.all()
        for station in stations:
            platforms = list(Platform.objects.filter(station=station))
            platform_count = len(platforms)

            if platform_count > 1:  # 如果车站有多个站台
                self.stdout.write(f"Processing {station.station_name} with {platform_count} platforms.")

                for i in range(platform_count):
                    for j in range(i + 1, platform_count):
                        platform1 = platforms[i]
                        platform2 = platforms[j]

                        # 获取平台所属线路名和车站名
                        line_name_1 = platform1.line.line_name
                        line_name_2 = platform2.line.line_name
                        station_name = station.station_name

                        # 检查换乘数据是否已经存在
                        if not Transfer.objects.filter(platform1=platform1, platform2=platform2).exists() and \
                           not Transfer.objects.filter(platform1=platform2, platform2=platform1).exists():
                            Transfer.objects.create(
                                platform1=platform1,
                                platform2=platform2,
                                transfer_time=5,
                                out_station=False
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created transfer from Line {line_name_1} to Line {line_name_2} at Station {station_name}."
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Transfer already exists between Line {line_name_1} and Line {line_name_2} at Station {station_name}."
                                )
                            )