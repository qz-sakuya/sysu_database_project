from django.core.management.base import BaseCommand, CommandError
from application01.models import Station, Exit
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Command(BaseCommand):
    help = 'Crawl exit information for the specified station'

    def handle(self, *args, **options):
        # 设置 Edge WebDriver 路径
        edge_driver_path = "D:\\edgedriver_win64\\edgedriver_win64\\msedgedriver.exe"  # 替换为您的 msedgedriver 实际路径

        # 配置 Edge 选项
        edge_options = Options()
        edge_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")

        # 初始化 WebDriver
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)

        try:
            # 特定车站信息
            specific_station_name = "𧒽岗"
            url = 'https://cs.gzmtr.com/ckfw/stationInfo/index.html?line_no=&station_name=%E8%99%AB%E9%9B%B7%20%E5%B2%97'

            try:
                # 尝试获取或创建车站对象
                station, created = Station.objects.get_or_create(station_name=specific_station_name)

                self.stdout.write(self.style.SUCCESS(f'Crawling exits for station: {station.station_name}'))

                fetch_station(driver, url, station, self.stdout, self.style)

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f'Failed to crawl exits for station: {specific_station_name}. Error: {e}'))
        except Exception as e:
            raise CommandError(f'An error occurred during the crawling process: {e}')
        finally:
            driver.quit()


def extract_text_hierarchy(element):
    current_level = {
        'text': '',
        'children': []
    }

    direct_texts = element.find_all(string=True, recursive=False)
    current_level['text'] = ' '.join([string.strip() for string in direct_texts if string.strip()])

    for child in element.children:
        if isinstance(child, Tag):
            child_result = extract_text_hierarchy(child)
            current_level['children'].append(child_result)
    return current_level


def fetch_station(driver, url, station, stdout, style):
    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        target_div = soup.find('div', {'id': 'tab_first', 'class': 'place_conntent_main'})

        if target_div:
            result = extract_text_hierarchy(target_div)

            exit_no = 1
            for station_exit in result['children']:
                name_div = station_exit['children'][0]
                exit_name = name_div['text']

                info_div = station_exit['children'][1]
                address_div = info_div['children'][0]
                exit_address = address_div['children'][0]['text']
                exit_sub_address = address_div['children'][1]['text'] if len(address_div['children']) > 1 else ''

                # Save the exit information to the database
                exit_instance = Exit.objects.create(
                    exit_no=exit_no,
                    station=station,
                    exit_name=exit_name,
                    exit_address=exit_address,
                    exit_sub_address=exit_sub_address
                )
                stdout.write(style.SUCCESS(
                    f'Successfully added exit: {exit_instance.exit_no} at station: {station.station_name}, '
                    f'exit name: {exit_instance.exit_name}, '
                    f'address: {exit_instance.exit_address}, '
                    f'sub-address: {exit_instance.exit_sub_address or "N/A"}'))
                exit_no += 1

        else:
            stdout.write(style.WARNING("Target div not found."))

    except Exception as e:
        print(f"An error occurred while processing station {station.station_name}: {e}")
        raise  # re-raise exception so it can be caught by the caller