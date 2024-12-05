# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_stations_for_line/<int:line_id>/', views.get_stations_for_line, name='get_stations_for_line'),
    path('get_stations_for_search/', views.get_stations_for_search, name='get_stations_for_search'),
    path('get_line_map/', views.get_line_map, name='get_line_map'),
    path('show_line_map/', views.show_line_map, name='show_line_map'),
]