# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_stations_for_line/<int:line_id>/', views.get_stations_for_line, name='get_stations_for_line'),
]