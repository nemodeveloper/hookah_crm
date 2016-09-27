import logging

from dateutil.relativedelta import relativedelta

import pyexcel

from django.db import transaction
from openpyxl import Workbook

from hookah_crm import settings
from src.apps.storage.exceptions import ParseProductStorageException
from src.apps.storage.models import Invoice, ProductStorage
from src.apps.storage.service import get_or_create_group, get_or_create_category, get_or_create_kind, \
    get_or_create_product, add_or_update_product_storage
from src.common_helper import date_to_verbose_format

logger = logging.getLogger('common_log')


class ProductStorageExcelProcessor(object):
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.errors = []
        self.file_types = ['xls', 'xlsx']

    def process(self):
        file_type = self.excel_file.name.split(".")[1]
        if file_type not in self.file_types:
            self.errors.append('Файл недопустимого формата, допустимые форматы - ' + str(self.file_types))
            return

        sheet = pyexcel.get_sheet(file_type=file_type, file_stream=self.excel_file.read())

        # пропускаем шапку
        head = True
        index = 1
        for row in sheet.rows():
            if not head:
                try:
                    index += 1
                    self.process_ps_excel_row(row)
                except Exception as e:
                    message = 'Ошибка при обработке строки файла номер ' + str(index) + ' данные строки - ' + str(row) + ' ошибка - ' + str(e)
                    logger.error(message)
                    self.errors.append(message)
            else:
                head = False

    @staticmethod
    def pre_process_row(row):
        if len(row) != 11:
            raise ParseProductStorageException(message=str(row) + ' - ' + u'в строке должно быть 11 столбцов')
        return ['0' if not item else item for item in row]  # пустые значения приравниваем к 0

    @transaction.atomic
    def process_ps_excel_row(self, row):
        logger.info("Начинаем обработку сырой строки - " + str(row))
        row = self.pre_process_row(row)
        logger.info("Строка после обработки - " + str(row))
        group = get_or_create_group(row[0])
        category = get_or_create_category(row[1], group)
        kind = get_or_create_kind(row[2], category)
        product = get_or_create_product(kind, row[3:9])
        add_or_update_product_storage(product, row[9:])
        logger.info("Строка успешно обработана!")

    def get_errors(self):
        return self.errors


class ExportProductStorageProcessor(object):

    def __init__(self, kinds):
        super(ExportProductStorageProcessor, self).__init__()
        self.kinds = kinds

    @staticmethod
    def post_process_sheet(sheet):
        dims = {}
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            sheet.column_dimensions[col].width = value + 3

    def generate_storage_file(self):

        products = ProductStorage.objects.select_related().filter(product__product_kind__in=self.kinds).filter(product_count__gt=0)
        book = Workbook()
        sheet = book.create_sheet(0)
        sheet.append(['Группа', 'Категория', 'Вид', 'Наименование', 'Остаток'])

        for product in products:
            kind = product.product.product_kind
            category = kind.product_category
            row = [category.product_group.group_name, category.category_name, kind.kind_name, product.product.product_name, product.product_count]
            sheet.append(row)
        self.post_process_sheet(sheet)
        return book


class InvoiceMonthReportProcessor(object):

    def __init__(self, start_date, end_date):
        self.amount = 0
        self.overhead = 0
        self.start_date = start_date
        self.end_date = end_date

        self.__process()

    def __str__(self):
        return 'Список приемки товара с %s по %s' % (date_to_verbose_format(self.start_date), date_to_verbose_format(self.end_date))

    def __process(self):
        self.invoices = Invoice.objects.filter(invoice_date__range=(self.start_date, self.end_date)).order_by('invoice_date')
        for invoice in self.invoices:
            self.amount += invoice.get_total_amount()
            self.overhead += invoice.overhead

