import logging


# Примись для логирования TODO добавить запись исключения при попытке записи в резервный лог
class LogViewMixin(object):

    def __init__(self):
        super(LogViewMixin, self).__init__()
        self.logger = logging.getLogger(self.log_name)

    log_name = 'common_log'

    def log_debug(self, message=''):
        try:
            self.logger.debug(msg=message)
        except Exception as e:
            pass

    def log_info(self, message=''):
        try:
            self.logger.info(msg=message)
        except Exception as e:
            pass

    def log_warning(self, message=''):
        try:
            self.logger.warning(msg=message)
        except Exception as e:
            pass

    def log_error(self, message=''):
        try:
            self.logger.error(msg=message)
        except Exception as e:
            pass

