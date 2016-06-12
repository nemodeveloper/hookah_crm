import socket

PRODUCTION = False if socket.gethostname() == 'DESKTOP-FIGNGVU' else True
SETTINGS_MODULE = 'hookah_crm.settings_prod' if PRODUCTION else 'hookah_crm.settings'
