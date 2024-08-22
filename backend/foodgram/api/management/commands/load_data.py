import csv

from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает данные из CSV файла в модель Ingredient'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='Путь к CSV файлу для загрузки данных')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)

                for row in reader:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )

            self.stdout.write(self.style.SUCCESS(
                'Данные успешно загружены из файла "%s"' % csv_file_path))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                'Файл не найден: "%s"' % csv_file_path))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке данных: {e}'))
