from __future__ import annotations
from qmonus_plugin_builder.module_libs import component as comp
from qmonus_sdk_plugins.libs.module_globals import *


# Define module metadata with 'ModuleHeader' class.
class ModuleHeader(comp.BaseHeader):
    def __setting__(self):
        return comp.Setting()


"""Write code below"""

USER_TYPE_MEMBER = 'member'
USER_TYPE_ADMIN = 'admin'
