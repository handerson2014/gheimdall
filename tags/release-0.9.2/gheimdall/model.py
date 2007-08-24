from turbogears.database import PackageHub
from sqlobject import *

hub = PackageHub('gheimdall')
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass

