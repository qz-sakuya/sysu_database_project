from django.core.management.base import BaseCommand, CommandError
from application01.models import Line, Platform, Section

class Command(BaseCommand):
    help = 'Check if there are sections between every two adjacent platforms of each line and print section_no'

    def handle(self, *args, **options):
        # 遍历所有线路
        for line in Line.objects.all().order_by('line_no'):
            self.stdout.write(f'Checking line: {line.line_name}')

            # 获取该线路的所有站台并按 platform_no 排序
            platforms = Platform.objects.filter(line=line).order_by('platform_no')

            # 如果没有站台，跳过这条线
            if not platforms.exists():
                self.stdout.write(self.style.WARNING(f'Line {line.line_name} has no platforms.'))
                continue

            previous_platform = None

            # 遍历站台，检查相邻站台间是否有区间
            for platform in platforms:
                if previous_platform is not None:
                    try:
                        # 尝试获取区间的记录
                        section = Section.objects.get(
                            line=line,
                            platform1=previous_platform,
                            platform2=platform
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'Section {section.section_no} exists between platform {previous_platform.platform_no} and {platform.platform_no} on line {line.line_name}.'
                        ))
                    except Section.DoesNotExist:
                        self.stdout.write(self.style.ERROR(
                            f'No section found between platform {previous_platform.platform_no} and {platform.platform_no} on line {line.line_name}. Please add a missing section.'
                        ))

                previous_platform = platform

            self.stdout.write(self.style.SUCCESS(f'Finished checking line: {line.line_name}'))