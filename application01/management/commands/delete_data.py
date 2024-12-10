from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, StationFacility

'''
命令行删除数据，示例：

删除线路数据
python manage.py delete_data delete_line "1号线"
（线路名）

删除车站数据
python manage.py delete_data delete_station "礌岗"
（车站名）

删除站台数据
python manage.py delete_data delete_platform "广佛线" "西塱"
（线路名，车站名）
注：根据车站名寻找站台

删除出口数据
python manage.py delete_data delete_exit "西塱" 1
（车站名，出口编号）

删除区间数据
python manage.py delete_data delete_section "1号线" 1
（线路名，区间编号）

删除换乘数据
python manage.py delete_data delete_transfer "1号线" "公园前" "2号线" "公园前"
（线路名1，线路名1上的车站名，线路名2，线路名2上的车站名）
注：根据车站名寻找站台

删除首班车数据
python manage.py delete_data delete_first_train "1号线" "西塱" down
（线路名，车站名，上下行）
注：根据车站名寻找站台

删除末班车数据
python manage.py delete_data delete_last_train "1号线" "广州东站" up
（线路名，站台名，上下行）
注：根据车站名寻找站台

删除设施标识数据
python manage.py delete_data delete_facility "广州东站" "机场"
（车站名，设施名）

'''


class Command(BaseCommand):
    help = 'Delete data from different models'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', required=True)

        # 删除线路数据的子命令
        delete_line_parser = subparsers.add_parser('delete_line', help='Delete a line')
        delete_line_parser.add_argument('line_name', type=str, help='The line name')

        # 删除站点数据的子命令
        delete_station_parser = subparsers.add_parser('delete_station', help='Delete a station')
        delete_station_parser.add_argument('station_name', type=str, help='The station name')

        # 删除站台数据的子命令
        delete_platform_parser = subparsers.add_parser('delete_platform', help='Delete a platform')
        delete_platform_parser.add_argument('line_name', type=str, help='The line name')
        delete_platform_parser.add_argument('station_name', type=str, help='The station name')

        # 删除出口数据的子命令
        delete_exit_parser = subparsers.add_parser('delete_exit', help='Delete an exit')
        delete_exit_parser.add_argument('station_name', type=str, help='The station name')
        delete_exit_parser.add_argument('exit_number', type=int, help='The exit number')

        # 删除区间数据的子命令
        delete_section_parser = subparsers.add_parser('delete_section', help='Delete a section')
        delete_section_parser.add_argument('line_name', type=str, help='The line name')
        delete_section_parser.add_argument('section_number', type=int, help='The section number')

        # 删除换乘数据的子命令
        delete_transfer_parser = subparsers.add_parser('delete_transfer', help='Delete a transfer')
        delete_transfer_parser.add_argument('line1_name', type=str, help='The first line name')
        delete_transfer_parser.add_argument('station1_name', type=str, help='The first station name')
        delete_transfer_parser.add_argument('line2_name', type=str, help='The second line name')
        delete_transfer_parser.add_argument('station2_name', type=str, help='The second station name')

        # 删除首班车数据的子命令
        delete_first_train_parser = subparsers.add_parser('delete_first_train', help='Delete a first train')
        delete_first_train_parser.add_argument('line_name', type=str, help='The line name')
        delete_first_train_parser.add_argument('station_name', type=str, help='The station name')
        delete_first_train_parser.add_argument('direction', type=str, choices=['up', 'down'], help='The direction (up/down)')

        # 删除末班车数据的子命令
        delete_last_train_parser = subparsers.add_parser('delete_last_train', help='Delete a last train')
        delete_last_train_parser.add_argument('line_name', type=str, help='The line name')
        delete_last_train_parser.add_argument('station_name', type=str, help='The station name')
        delete_last_train_parser.add_argument('direction', type=str, choices=['up', 'down'], help='The direction (up/down)')

        # 删除设施标识数据的子命令
        delete_facility_parser = subparsers.add_parser('delete_facility', help='Delete a facility')
        delete_facility_parser.add_argument('station_name', type=str, help='The station name')
        delete_facility_parser.add_argument('facility_type', type=str, help='The facility type')

    def handle(self, *args, **options):
        command = options['command']

        if command == 'delete_line':
            self.delete_line(options)
        elif command == 'delete_station':
            self.delete_station(options)
        elif command == 'delete_platform':
            self.delete_platform(options)
        elif command == 'delete_exit':
            self.delete_exit(options)
        elif command == 'delete_section':
            self.delete_section(options)
        elif command == 'delete_transfer':
            self.delete_transfer(options)
        elif command == 'delete_first_train':
            self.delete_first_train(options)
        elif command == 'delete_last_train':
            self.delete_last_train(options)
        elif command == 'delete_facility':
            self.delete_facility(options)

    def delete_line(self, options):
        line_name = options['line_name']
        try:
            line = Line.objects.get(line_name=line_name)
            line.delete()
            self.stdout.write(self.style.SUCCESS(f"Line '{line_name}' has been deleted"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line_name}' does not exist"))

    def delete_station(self, options):
        station_name = options['station_name']
        try:
            station = Station.objects.get(station_name=station_name)
            station.delete()
            self.stdout.write(self.style.SUCCESS(f"Station '{station_name}' has been deleted"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))

    def delete_platform(self, options):
        line_name = options['line_name']
        station_name = options['station_name']
        try:
            station = Station.objects.get(station_name=station_name)
            line = Line.objects.get(line_name=line_name)
            platform = Platform.objects.get(line=line, station=station)
            platform.delete()
            self.stdout.write(self.style.SUCCESS(f"Platform '{station_name}' on line '{line_name}' has been deleted"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line_name}' does not exist"))
        except Platform.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Platform '{station_name}' on line '{line_name}' does not exist"))

    def delete_exit(self, options):
        station_name = options['station_name']
        exit_number = options['exit_number']
        try:
            station = Station.objects.get(station_name=station_name)
            exit = Exit.objects.get(station=station, exit_no=exit_number)
            exit.delete()
            self.stdout.write(self.style.SUCCESS(f"Exit {exit_number} at station '{station_name}' has been deleted"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))
        except Exit.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Exit {exit_number} at station '{station_name}' does not exist"))

    def delete_section(self, options):
        line_name = options['line_name']
        section_number = options['section_number']
        try:
            line = Line.objects.get(line_name=line_name)
            section = Section.objects.get(line=line, section_no=section_number)
            section.delete()
            self.stdout.write(self.style.SUCCESS(f"Section {section_number} on line '{line_name}' has been deleted"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line_name}' does not exist"))
        except Section.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Section {section_number} on line '{line_name}' does not exist"))

    def delete_transfer(self, options):
        line1_name = options['line1_name']
        station1_name = options['station1_name']
        line2_name = options['line2_name']
        station2_name = options['station2_name']
        try:
            station1 = Station.objects.get(station_name=station1_name)
            station2 = Station.objects.get(station_name=station2_name)
            line1 = Line.objects.get(line_name=line1_name)
            line2 = Line.objects.get(line_name=line2_name)
            platform1 = Platform.objects.get(line=line1, station=station1)
            platform2 = Platform.objects.get(line=line2, station=station2)
            transfer = Transfer.objects.get(platform1=platform1, platform2=platform2)
            transfer.delete()
            self.stdout.write(self.style.SUCCESS(
                f"Transfer data has been deleted: Platform '{station1_name}' on line '{line1_name}' to Platform '{station2_name}' on line '{line2_name}'"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station1_name}' or '{station2_name}' does not exist"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line1_name}' or '{line2_name}' does not exist"))
        except Platform.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Platform does not exist: Platform '{station1_name}' on line '{line1_name}' or Platform '{station2_name}' on line '{line2_name}'"))
        except Transfer.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Transfer data does not exist: Platform '{station1_name}' on line '{line1_name}' to Platform '{station2_name}' on line '{line2_name}'"))

    def delete_first_train(self, options):
        line_name = options['line_name']
        station_name = options['station_name']
        direction = options['direction']
        try:
            station = Station.objects.get(station_name=station_name)
            line = Line.objects.get(line_name=line_name)
            platform = Platform.objects.get(line=line, station=station)
            first_train = FirstTrain.objects.get(platform=platform, direction=direction)
            first_train.delete()
            self.stdout.write(self.style.SUCCESS(
                f"First train data has been deleted: Platform '{station_name}' on line '{line_name}' ({direction})"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line_name}' does not exist"))
        except Platform.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Platform does not exist: Platform '{station_name}' on line '{line_name}'"))
        except FirstTrain.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"First train data does not exist: Platform '{station_name}' on line '{line_name}' ({direction})"))

    def delete_last_train(self, options):
        line_name = options['line_name']
        station_name = options['station_name']
        direction = options['direction']
        try:
            station = Station.objects.get(station_name=station_name)
            line = Line.objects.get(line_name=line_name)
            platform = Platform.objects.get(line=line, station=station)
            last_train = LastTrain.objects.get(platform=platform, direction=direction)
            last_train.delete()
            self.stdout.write(self.style.SUCCESS(
                f"Last train data has been deleted: Platform '{station_name}' on line '{line_name}' ({direction})"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))
        except Line.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Line '{line_name}' does not exist"))
        except Platform.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Platform does not exist: Platform '{station_name}' on line '{line_name}'"))
        except LastTrain.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Last train data does not exist: Platform '{station_name}' on line '{line_name}' ({direction})"))

    def delete_facility(self, options):
        station_name = options['station_name']
        facility_type = options['facility_type']
        try:
            station = Station.objects.get(station_name=station_name)
            facility = StationFacility.objects.get(station=station, facility_type=facility_type)
            facility.delete()
            self.stdout.write(self.style.SUCCESS(
                f"Facility data has been deleted: Facility '{facility_type}' at station '{station_name}'"))
        except Station.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Station '{station_name}' does not exist"))
        except StationFacility.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Facility data does not exist: Facility '{facility_type}' at station '{station_name}'"))