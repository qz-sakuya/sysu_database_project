from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, \
    StationFacility, Image

'''
命令行添加数据，示例： 

添加线路数据
python manage.py add_data add_line "3.5" "3号线北延段" "#00629B"
python manage.py add_data add_line "21" "21号线" "1b1752"
（线路编号，线路名，标识色）

添加站点数据
python manage.py add_data add_station "西塱"

添加站台数据
python manage.py add_data add_platform "1号线" 1 "西塱"
（线路名，站台编号，所处车站名）

添加出口数据
python manage.py add_data add_exit "西塱" 1 "A出口" "西塱街道" --exit_sub_address="东侧"
（车站名，出口编号，出口名称，地址，子地址）

添加区间数据
python manage.py add_data add_section "1号线" 1 "西塱" "坑口" 5 3.5
（线路名，区间编号，车站名1，车站名2，时间，费用）
注：根据车站名寻找站台

添加换乘数据
python manage.py add_data add_transfer "1号线" "公园前" "2号线" "公园前" 5  --out_station
（线路名1，线路名1上的车站名，线路名2，线路名2上的车站名，换乘时间，是否出站）
注：根据车站名寻找站台

添加首班车数据
python manage.py add_data add_first_train "1号线" "西塱" up 06:00
（线路名，车站名，上下行，时间）
注：根据车站名寻找站台

添加末班车数据
python manage.py add_data add_last_train "1号线" "西塱" down 23:00
（线路名，站台名，上下行，时间）
注：根据车站名寻找站台

添加设施标识数据
python manage.py add_data add_facility "广州东站" "火车站" --image_name="railway"
（车站名，设施名，图片名）

'''


class Command(BaseCommand):
    help = 'Add data to different models'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', required=True)

        # 添加线路数据的子命令
        add_line_parser = subparsers.add_parser('add_line', help='Add a new line')
        add_line_parser.add_argument('line_no', type=str, help='The line number')
        add_line_parser.add_argument('line_name', type=str, help='The line name')
        add_line_parser.add_argument('colour', type=str, help='The colour of the line (Pantone color code)')

        # 添加站点数据的子命令
        add_station_parser = subparsers.add_parser('add_station', help='Add a new station')
        add_station_parser.add_argument('station_name', type=str, help='The station name')

        # 添加站台数据的子命令
        add_platform_parser = subparsers.add_parser('add_platform', help='Add a new platform')
        add_platform_parser.add_argument('line_name', type=str, help='The line name')
        add_platform_parser.add_argument('platform_no', type=int, help='The platform number')
        add_platform_parser.add_argument('station_name', type=str, help='The station name')

        # 添加出口数据的子命令
        add_exit_parser = subparsers.add_parser('add_exit', help='Add a new exit')
        add_exit_parser.add_argument('station_name', type=str, help='The station name')
        add_exit_parser.add_argument('exit_no', type=int, help='The exit number')
        add_exit_parser.add_argument('exit_name', type=str, help='The exit name')
        add_exit_parser.add_argument('address', type=str, help='The exit address')
        add_exit_parser.add_argument('--exit_sub_address', type=str, default='', help='The exit sub-address (optional)')

        # 添加区间数据的子命令
        add_section_parser = subparsers.add_parser('add_section', help='Add a new section')
        add_section_parser.add_argument('line_name', type=str, help='The line name')
        add_section_parser.add_argument('section_no', type=int, help='The section number')
        add_section_parser.add_argument('station1_name', type=str, help='The first station name')
        add_section_parser.add_argument('station2_name', type=str, help='The second station name')
        add_section_parser.add_argument('travel_time', type=int, help='The travel time in minutes')
        add_section_parser.add_argument('fare', type=float, help='The fare in yuan')

        # 添加换乘数据的子命令
        add_transfer_parser = subparsers.add_parser('add_transfer', help='Add a new transfer')
        add_transfer_parser.add_argument('line1_name', type=str, help='The first line name')
        add_transfer_parser.add_argument('station1_name', type=str, help='The first station name')
        add_transfer_parser.add_argument('line2_name', type=str, help='The second line name')
        add_transfer_parser.add_argument('station2_name', type=str, help='The second station name')
        add_transfer_parser.add_argument('transfer_time', type=int, help='The transfer time in minutes')
        add_transfer_parser.add_argument('--out_station', action='store_true', help='Indicate if out-station transfer (optional)')

        # 添加首班车数据的子命令
        add_first_train_parser = subparsers.add_parser('add_first_train', help='Add a new first train')
        add_first_train_parser.add_argument('line_name', type=str, help='The line name')
        add_first_train_parser.add_argument('station_name', type=str, help='The station name')
        add_first_train_parser.add_argument('direction', type=str, choices=['up', 'down'], help='The direction (up/down)')
        add_first_train_parser.add_argument('time', type=str, help='The first train time (HH:MM)')

        # 添加末班车数据的子命令
        add_last_train_parser = subparsers.add_parser('add_last_train', help='Add a new last train')
        add_last_train_parser.add_argument('line_name', type=str, help='The line name')
        add_last_train_parser.add_argument('station_name', type=str, help='The station name')
        add_last_train_parser.add_argument('direction', type=str, choices=['up', 'down'], help='The direction (up/down)')
        add_last_train_parser.add_argument('time', type=str, help='The last train time (HH:MM)')

        # 添加设施标识数据的子命令
        add_facility_parser = subparsers.add_parser('add_facility', help='Add a new facility')
        add_facility_parser.add_argument('station_name', type=str, help='The station name')
        add_facility_parser.add_argument('facility_type', type=str, help='The facility name')
        add_facility_parser.add_argument('--image_name', type=str, default=None, help='The icon image URL (optional)')

    def handle(self, *args, **options):
        command = options['command']

        if command == 'add_line':
            self.add_line(options)
        elif command == 'add_station':
            self.add_station(options)
        elif command == 'add_platform':
            self.add_platform(options)
        elif command == 'add_exit':
            self.add_exit(options)
        elif command == 'add_section':
            self.add_section(options)
        elif command == 'add_transfer':
            self.add_transfer(options)
        elif command == 'add_first_train':
            self.add_first_train(options)
        elif command == 'add_last_train':
            self.add_last_train(options)
        elif command == 'add_facility':
            self.add_facility(options)

    def add_line(self, options):
        line_no = options['line_no']
        line_name = options['line_name']
        colour = options['colour']

        try:
            line = Line.objects.create(
                line_no=line_no,
                line_name=line_name,
                colour=colour,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added line: {line.line_name}'))
        except Exception as e:
            raise CommandError(f'Failed to add line: {e}')

    def add_station(self, options):
        station_name = options['station_name']

        try:
            station = Station.objects.create(station_name=station_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully added station: {station.station_name}'))
        except Exception as e:
            raise CommandError(f'Failed to add station: {e}')

    def add_platform(self, options):
        line_name = options['line_name']
        platform_no = options['platform_no']
        station_name = options['station_name']

        try:
            line = Line.objects.get(line_name=line_name)
            station = Station.objects.get(station_name=station_name)
            platform = Platform.objects.create(
                platform_no=platform_no,
                line=line,
                station=station
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added platform: {platform.platform_no} on line {line.line_name} at station {station.station_name}'))
        except Line.DoesNotExist:
            raise CommandError(f'Line with name {line_name} does not exist')
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add platform: {e}')

    def add_exit(self, options):
        station_name = options['station_name']
        exit_no = options['exit_no']
        exit_name = options['exit_name']
        address = options['address']
        exit_sub_address = options['exit_sub_address']

        try:
            station = Station.objects.get(station_name=station_name)
            exit_obj = Exit.objects.create(
                exit_no=exit_no,
                exit_name=exit_name,
                address=address,
                exit_sub_address=exit_sub_address,
                station=station
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added exit: {exit_obj.exit_name} at station {station.station_name}'))
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add exit: {e}')

    def add_section(self, options):
        line_name = options['line_name']
        section_no = options['section_no']
        station1_name = options['station1_name']
        station2_name = options['station2_name']
        travel_time = options['travel_time']
        fare = options['fare']

        try:
            line = Line.objects.get(line_name=line_name)
            station1 = Station.objects.get(station_name=station1_name)
            station2 = Station.objects.get(station_name=station2_name)
            platform1 = Platform.objects.filter(line=line, station=station1).first()
            platform2 = Platform.objects.filter(line=line, station=station2).first()

            if not platform1 or not platform2:
                raise CommandError(f'No platform found for station {station1_name} or {station2_name} on line {line_name}')

            section = Section.objects.create(
                section_no=section_no,
                line=line,
                platform1=platform1,
                platform2=platform2,
                travel_time=travel_time,
                fare=fare
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added section: {section.section_no} from {station1.station_name} to {station2.station_name} on line {line.line_name}'))
        except Line.DoesNotExist:
            raise CommandError(f'Line with name {line_name} does not exist')
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station1_name} or {station2_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add section: {e}')

    def add_transfer(self, options):
        line1_name = options['line1_name']
        station1_name = options['station1_name']
        line2_name = options['line2_name']
        station2_name = options['station2_name']
        transfer_time = options['transfer_time']
        out_station = options['out_station']

        try:
            line1 = Line.objects.get(line_name=line1_name)
            line2 = Line.objects.get(line_name=line2_name)
            station1 = Station.objects.get(station_name=station1_name)
            station2 = Station.objects.get(station_name=station2_name)
            platform1 = Platform.objects.filter(line=line1, station=station1).first()
            platform2 = Platform.objects.filter(line=line2, station=station2).first()

            if not platform1 or not platform2:
                raise CommandError(f'No platform found for station {station1_name} on line {line1_name} or station {station2_name} on line {line2_name}')

            transfer = Transfer.objects.create(
                platform1=platform1,
                platform2=platform2,
                transfer_time=transfer_time,
                out_station=out_station
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added transfer: from {station1.station_name} on line {line1.line_name} to {station2.station_name} on line {line2.line_name}'))
        except Line.DoesNotExist:
            raise CommandError(f'Line with name {line1_name} or {line2_name} does not exist')
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station1_name} or {station2_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add transfer: {e}')

    def add_first_train(self, options):
        line_name = options['line_name']
        station_name = options['station_name']
        direction = options['direction']
        time = options['time']

        try:
            line = Line.objects.get(line_name=line_name)
            station = Station.objects.get(station_name=station_name)
            platform = Platform.objects.filter(line=line, station=station).first()

            if not platform:
                raise CommandError(f'No platform found for station {station_name} on line {line_name}')

            first_train = FirstTrain.objects.create(
                platform=platform,
                direction=direction,
                departure_time=time
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added first train: {direction} direction at {time} from station {station.station_name} on line {line.line_name}'))
        except Line.DoesNotExist:
            raise CommandError(f'Line with name {line_name} does not exist')
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add first train: {e}')

    def add_last_train(self, options):
        line_name = options['line_name']
        station_name = options['station_name']
        direction = options['direction']
        time = options['time']

        try:
            line = Line.objects.get(line_name=line_name)
            station = Station.objects.get(station_name=station_name)
            platform = Platform.objects.filter(line=line, station=station).first()

            if not platform:
                raise CommandError(f'No platform found for station {station_name} on line {line_name}')

            last_train = LastTrain.objects.create(
                platform=platform,
                direction=direction,
                departure_time=time
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully added last train: {direction} direction at {time} from station {station.station_name} on line {line.line_name}'))
        except Line.DoesNotExist:
            raise CommandError(f'Line with name {line_name} does not exist')
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station_name} does not exist')
        except Exception as e:
            raise CommandError(f'Failed to add last train: {e}')

    def add_facility(self, options):
        station_name = options['station_name']
        facility_type = options['facility_type']
        image_name = options['image_name']

        try:
            station = Station.objects.get(station_name=station_name)
        except Station.DoesNotExist:
            raise CommandError(f'Station with name {station_name} does not exist')

        icon_image = None
        if image_name:
            try:
                icon_image = Image.objects.get(image_name=image_name)
            except Image.DoesNotExist:
                raise CommandError(f'Image with name {image_name} does not exist')

        try:
            facility = StationFacility.objects.create(
                station=station,
                facility_type=facility_type,
                icon_image=icon_image
            )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully added facility: {facility.facility_type} at station {station.station_name}'))
        except Exception as e:
            raise CommandError(f'Failed to add facility: {e}')




