

# Базовые исключение при парсинге файла
class ParseFileException(ValueError):

    def __init__(self, message, *args, **kwargs):
        super(ParseFileException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message
