from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, StationFacility


'''
编写自定义命令并运行

python manage.py test_cmds "18号线" "#1f4db6"
'''
class Command(BaseCommand):
    help = 'Changes the colour of a specified line by its name'

    def add_arguments(self, parser):
        parser.add_argument('line_name', type=str, help='The name of the line to change')
        parser.add_argument('new_colour', type=str, help='The new colour to set')

    def handle(self, *args, **options):
        line_name = options['line_name']
        new_colour = options['new_colour']

        try:
            line = Line.objects.get(line_name=line_name)
            line.colour = new_colour
            line.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully changed colour for line '{line_name}' to '{new_colour}'."))
        except Line.DoesNotExist:
            raise CommandError(f"Line with name '{line_name}' does not exist.")