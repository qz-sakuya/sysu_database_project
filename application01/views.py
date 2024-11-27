# application01/views.py
from operator import itemgetter

from django.http import JsonResponse
from django.shortcuts import render

# views.py
from django.shortcuts import render
from django.core.management.base import BaseCommand, CommandError
import base64

from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, StationFacility

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
def get_stations_for_line(request, line_id):
    if request.method == 'GET':
        try:
            current_line = Line.objects.get(id=line_id)
            platforms = Platform.objects.filter(line=current_line).order_by('-platform_no')

            # 获取每个车站经过的所有线路及其标识色和线路编号
            station_list = []
            for platform in platforms:
                station = platform.station
                lines_through_station = Platform.objects.filter(station=station).values('line__id', 'line__colour',
                                                                                        'line__line_no').distinct().order_by(
                    'line__line_no')
                lines_data = [dict(line) for line in lines_through_station]

                # 修正3北和14支编号
                for line in lines_data:
                    if line['line__line_no'] == '3.5':
                        line['line__line_no'] = '3'

                # 去重
                seen = set()
                unique_lines_data = []
                for line in lines_data:
                    key = (line['line__id'], line['line__line_no'])
                    if key not in seen:
                        seen.add(key)
                        unique_lines_data.append(line)
                lines_data = unique_lines_data

                # 将当前查询的线路提前
                lines_data.sort(key=lambda x: (x['line__id'] != current_line.id, x['line__line_no']))

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
                    'facilities': facility_data
                })
            return JsonResponse({'stations': station_list})
        except Line.DoesNotExist:
            return JsonResponse({'error': 'Line not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
