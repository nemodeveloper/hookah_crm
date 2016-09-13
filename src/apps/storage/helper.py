import logging

from dateutil.relativedelta import relativedelta

import pyexcel

from django.db import transaction

from hookah_crm import settings
from src.apps.storage.exceptions import ParseProductStorageException
from src.apps.storage.models import Invoice
from src.apps.storage.service import get_or_create_group, get_or_create_category, get_or_create_kind, \
    get_or_create_product, add_or_update_product_storage


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

    def preprocess_row(self, row):
        if len(row) != 12:
            raise ParseProductStorageException(message=str(row) + ' - ' + u'в строке должно быть 12 столбцов')
        return ['0' if not item else item for item in row]  # пустые значения приравниваем к 0

    @transaction.atomic
    def process_ps_excel_row(self, row):
        logger.info("Начинаем обработку сырой строки - " + str(row))
        row = self.preprocess_row(row)
        logger.info("Строка после обработки - " + str(row))
        group = get_or_create_group(row[0])
        category = get_or_create_category(row[1], group)
        kind = get_or_create_kind(row[2], category)
        product = get_or_create_product(kind, row[3:10])
        add_or_update_product_storage(product, row[10:])
        logger.info("Строка успешно обработана!")

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

