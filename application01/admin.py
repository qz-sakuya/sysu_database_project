from django.contrib import admin
from .models import Image, Line, Station, Platform, Exit, Section, Transfer, FirstTrain, LastTrain, StationFacility

admin.site.register(Image)
admin.site.register(Line)
admin.site.register(Station)
admin.site.register(Platform)
admin.site.register(Exit)
admin.site.register(Section)
admin.site.register(Transfer)
admin.site.register(FirstTrain)
admin.site.register(LastTrain)
admin.site.register(StationFacility)