# application01/views.py
from operator import itemgetter

from django.http import JsonResponse
from django.shortcuts import render

# views.py
from django.shortcuts import render
from django.core.management.base import BaseCommand, CommandError
import base64

from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, \
    StationFacility


# 初始视图
def index(request):
    # 获取线路，排除3北
    lines = Line.objects.exclude(line_no=3.5).order_by('line_no')

    # 获取每条线路的起终点站
    for line in lines:
        platforms = Platform.objects.filter(line=line).order_by('platform_no')
        if platforms.exists():
            min_platform = platforms.first()
            max_platform = platforms.last()

            line.min_station_name = min_platform.station.station_name
            line.max_station_name = max_platform.station.station_name
        else:
            line.min_station_name = ''
            line.max_station_name = ''

    context = {
        'lines': lines,
    }
    return render(request, 'application01/index.html', context)


# 点击线路项-显示车站列表
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import base64

def get_stations_for_line(request, line_id):
    if request.method == 'GET':
        try:
            current_line = Line.objects.get(id=line_id)
            platforms = Platform.objects.filter(line=current_line).order_by('-platform_no')

            # 创建一个线路到终点站的字典
            line_endpoints = {}

            # 获取每个车站经过的所有线路及其标识色和线路编号
            station_list = []
            for platform in platforms:
                # 从站台获取车站
                station = platform.station

                # 获取车站具有的站台和线路
                have_platforms = Platform.objects.filter(station=station)
                have_lines = Line.objects.filter(platform__in=have_platforms).distinct()

                # 更新线路到终点站的字典
                for line in have_lines:
                    if line.id not in line_endpoints:
                        platforms = Platform.objects.filter(line=line.id).order_by('platform_no')
                        if platforms.exists():
                            min_platform = platforms.first()
                            max_platform = platforms.last()
                            line_endpoints[line.id] = {
                                'min_station_name': min_platform.station.station_name,
                                'max_station_name': max_platform.station.station_name
                            }
                        else:
                            line_endpoints[line.id] = {
                                'min_station_name': '',
                                'max_station_name': ''
                            }

                # 获取车站的首末班车数据
                first_trains_data = []
                last_trains_data = []
                for plat in have_platforms:

                    first_train = FirstTrain.objects.filter(platform=plat)
                    for train in first_train:
                        if train.direction == 'up':
                            direction_name = line_endpoints[plat.line_id]['max_station_name'] or '上行'
                        else:
                            direction_name = line_endpoints[plat.line_id]['min_station_name'] or '下行'
                        departure_time_str = train.departure_time.strftime('%H:%M') if train.departure_time else None
                        first_trains_data.append({
                            'direction': direction_name,
                            'departure_time': departure_time_str
                        })

                    last_train = LastTrain.objects.filter(platform=plat)  # 假设LastTrain模型存在
                    for train in last_train:
                        if train.direction == 'up':
                            direction_name = line_endpoints[plat.line_id]['max_station_name'] or '上行'
                        else:
                            direction_name = line_endpoints[plat.line_id]['min_station_name'] or '下行'
                        departure_time_str = train.departure_time.strftime('%H:%M') if train.departure_time else None
                        last_trains_data.append({
                            'direction': direction_name,
                            'departure_time': departure_time_str
                        })

                # 将线路数据转为字典
                lines_data = [
                    {
                        'id': line.id,
                        'colour': line.colour,
                        'line_no': line.line_no,
                    }
                    for line in have_lines
                ]

                # 修正3北和14支线路编号
                for line in lines_data:
                    if line['line_no'] == '3.5':
                        line['line_no'] = '3'

                # 去重
                seen = set()
                unique_lines_data = []
                for line in lines_data:
                    key = (line['id'], line['line_no'])
                    if key not in seen:
                        seen.add(key)
                        unique_lines_data.append(line)
                lines_data = unique_lines_data

                # 将当前查询的线路提前
                lines_data.sort(key=lambda x: (x['id'] != current_line.id, x['line_no']))

                # 获取车站的设施信息
                facilities = StationFacility.objects.filter(station=station).select_related('icon_image').order_by(
                    '-facility_type')

                facility_data = [
                    {
                        'facility_type': facility.facility_type,
                        'icon_image_data': base64.b64encode(facility.icon_image.image_data).decode(
                            'utf-8') if facility.icon_image else None
                    }
                    for facility in facilities
                ]

                station_list.append({
                    'name': station.station_name,
                    'lines': lines_data,
                    'facilities': facility_data,
                    'first_trains': first_trains_data,
                    'last_trains': last_trains_data
                })
            return JsonResponse({'stations': station_list})
        except Line.DoesNotExist:
            return JsonResponse({'error': 'Line not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)