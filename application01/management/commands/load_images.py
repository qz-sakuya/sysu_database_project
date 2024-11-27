import os
from django.core.management.base import BaseCommand
from application01.models import Image

'''

命令行读取图片，示例：
python manage.py load_images "D:\Desktop\数据库大作业\图片\intercity.png"

'''


class Command(BaseCommand):
    help = 'Load a single image and save it to the database'

    def add_arguments(self, parser):
        parser.add_argument('image_path', type=str, help='The path to the image file')

    def handle(self, *args, **options):
        image_path = options['image_path']

        # 检查文件是否存在
        if not os.path.isfile(image_path):
            self.stdout.write(self.style.ERROR(f"The provided path '{image_path}' is not a valid file."))
            return

        # 获取文件名和扩展名
        filename = os.path.basename(image_path)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            self.stdout.write(self.style.ERROR(f"Unsupported file format: {filename}"))
            return

        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_name = os.path.splitext(filename)[0]  # 使用文件名作为image_name
            image = Image(image_data=image_data, image_name=image_name)
            image.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully saved {filename} to the database."))