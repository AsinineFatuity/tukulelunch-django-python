#use this to change between local and production settings files

# from .production_settings import *

try:
    from .local_settings import *
except:
    pass