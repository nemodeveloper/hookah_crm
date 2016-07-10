

# Исключение возникающие при парсинге excel файла остатков
class ParseProductStorageException(ValueError):

    def __init__(self, message, *args, **kwargs):
        super(ParseProductStorageException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message
