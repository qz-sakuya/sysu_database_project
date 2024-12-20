# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_stations_for_search/', views.get_stations_for_search, name='get_stations_for_search'),
    path('get_line_map/', views.get_line_map, name='get_line_map'),
    path('show_line_map/', views.show_line_map, name='show_line_map'),
    path('get_stations_for_line/<str:line_no>/', views.get_stations_for_line, name='get_stations_for_line'),
    path('calculate_path/<str:start_station_name>/<str:end_station_name>/<str:search_type>/', views.calculate_path, name='calculate_path'),
    path('station-info/<str:station_name>/', views.station_info_view, name='station_info'),
]