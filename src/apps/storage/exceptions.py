
from src.base_components.exceptions import ParseFileException


# Исключение возникающие при парсинге excel файла остатков
class ParseProductException(ParseFileException):

    def __init__(self, message, *args, **kwargs):
        super(ParseProductException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message
