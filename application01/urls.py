# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_stations_for_search/', views.get_stations_for_search, name='get_stations_for_search'),
    path('line_map/', views.show_line_map, name='show_line_map'),
    path('get_line_map/', views.get_line_map, name='get_line_map'),
    path('get_stations_for_line/<str:line_no>/', views.get_stations_for_line, name='get_stations_for_line'),
    path('calculate_path/<str:start_station_name>/<str:end_station_name>/<str:search_type>/', views.calculate_path, name='calculate_path'),
    path('station/<str:station_name>/', views.show_station_info, name='show_station_info'),
    path('get_station_info/<str:station_name>/', views.get_station_info, name='get_station_info'),
]