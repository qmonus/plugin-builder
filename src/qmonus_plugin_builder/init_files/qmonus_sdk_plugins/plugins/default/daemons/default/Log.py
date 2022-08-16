from __future__ import annotations
from qmonus_plugin_builder.daemon_libs import component as comp
from qmonus_sdk_plugins.libs.daemon_globals import *


# Define daemon metadata (status, interval, etc.) with 'DaemonHeader' class.
class DaemonHeader(comp.BaseHeader):
    def __setting__(self):
        return comp.Setting(status='active', interval=60)


# Define global variables.
# data: str = comp.global_variable()


# Define daemon commands with 'Command{0, 1, 2, ...}' classes.
# Command class must inherit 'Script'.
class Command0(comp.Script):
    def __setting__(self):
        return comp.ScriptSetting(label='0')

    async def code(self):
        logger.info('executed!!')
