from dateutil.relativedelta import relativedelta

import pyexcel
from django.db import transaction

from hookah_crm import settings
from src.apps.storage.exceptions import ParseProductStorageException
from src.apps.storage.models import Invoice
from src.apps.storage.service import get_or_create_group, get_or_create_category, get_or_create_kind, \
    get_or_create_product, add_or_update_product_storage


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
        index = 2
        for row in sheet.rows():
            if not head:
                try:
                    self.process_ps_excel_row(row)
                    index += 1
                except Exception as e:
                    self.errors.append('Ошибка при обработке строки файла номер ' + str(index) + ' данные строки - ' + str(row) + ' ошибка - ' + str(e))
            else:
                head = False

    def preprocess_row(self, row):
        if len(row) != 12:
            raise ParseProductStorageException(message=str(row) + ' - ' + u'в строке должно быть 12 столбцов')

        for item in row:
            if isinstance(item, str):
                item.strip()
            if not item:
                raise ParseProductStorageException(message='В строке есть не заполненые столбцы!')
        return row

    @transaction.atomic
    def process_ps_excel_row(self, row):
        row = self.preprocess_row(row)
        group = get_or_create_group(row[0])
        category = get_or_create_category(row[1], group)
        kind = get_or_create_kind(row[2], category)
        product = get_or_create_product(kind, row[3:10])
        add_or_update_product_storage(product, row[10:])

    def get_errors(self):
        return self.errors


class InvoiceMonthReportProcessor(object):

    def __init__(self, date):
        self.amount = 0
        self.overhead = 0
        self.first_day = date + relativedelta(day=1)
        self.last_day = date + relativedelta(day=1, months=+1, days=-1)

        self.__process()

    def __str__(self):
        return 'Период с %s по %s' % (self.first_day.strftime(settings.SHORT_DATE_FORMAT),
                                      self.last_day.strftime(settings.SHORT_DATE_FORMAT))

    def __process(self):
        self.invoices = Invoice.objects.filter(invoice_date__range=(self.first_day, self.last_day)).order_by('invoice_date')
        for invoice in self.invoices:
            self.amount += invoice.get_total_amount()
            self.overhead += invoice.overhead

