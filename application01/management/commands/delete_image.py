from django.core.management.base import BaseCommand
from application01.models import Image  # 替换your_app为实际的app名称
from django.core.exceptions import ObjectDoesNotExist

'''

命令行删除图片，示例：
python manage.py delete_image intercity

'''

class Command(BaseCommand):
    help = 'Delete an image from the database by its name'

    def add_arguments(self, parser):
        parser.add_argument('image_name', type=str, help='The name of the image to delete')

    def handle(self, *args, **options):
        image_name = options['image_name']
        try:
            image = Image.objects.get(image_name=image_name)
            image.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {image_name} from the database."))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING(f"No image found with the name '{image_name}'"))