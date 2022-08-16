INIT_TEMPLATE = """##########################
# Automatically generated
##########################

"""


SCENARIO_CONTEXT_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.scenario_context import (
    axis,
    qmonus,
    session,
    resources,
    params,
    request,
)
from .module import *

"""


DAEMON_CONTEXT_TEMPLATE = """##########################
# Automatically generated
##########################

from .module import *

"""


CLASS_CONTEXT_TEMPLATE = """##########################
# Automatically generated
##########################

from .module import *

"""


MODULE_CONTEXT_TEMPLATE = """##########################
# Automatically generated
##########################

from .module import *

"""


SCENARIO_GLOBALS_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.scenario_globals import *
from . import scenario_context as context, atom, model

"""


DAEMON_GLOBALS_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.daemon_globals import *
from . import daemon_context as context, atom, model

"""


CLASS_GLOBALS_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.class_globals import *
from . import class_context as context, atom, model

"""


MODULE_GLOBALS_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.module_globals import *
from . import module_context as context, atom, model

"""


ATOM_TEMPLATE = """##########################
# Automatically generated
##########################

{% for import_stmt in import_stmts %}
{{ import_stmt }}
{% endfor %}

"""


MODEL_TEMPLATE = """##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.model import aiodb

import sqlalchemy

metadata = sqlalchemy.MetaData()


{% for class_name in class_names %}
{{ class_name }} = sqlalchemy.Table("{{ class_name }}", metadata)

{% endfor %}

"""


MODULE_TEMPLATE = """##########################
# Automatically generated
##########################

{% for import_stmt in import_stmts %}
{{ import_stmt }}
{% endfor %}

"""


CLASSES_INITIAL_TEMPLATE = """##########################
# Automatically generated
##########################

from __future__ import annotations
from qmonus_plugin_builder.class_libs import component as comp


{% for class_name in class_names %}
class {{ class_name }}(comp.BaseClass):
    pass


{% endfor %}

"""


CLASSES_FULL_TEMPLATE = """##########################
# Automatically generated
##########################

from __future__ import annotations
import typing
from qmonus_plugin_builder.class_libs import component as comp
from qmonus_sdk_plugins.libs.class_globals import *


{% for class_definition in class_definitions %}
class {{ class_definition.name }}(
    {% for extend in class_definition.extends %}
    {{ extend }},
    {% endfor %}
):
    def __init__(
        self,
        {% for variable in class_definition.variables_without_defaults %}
        {{ variable.name }}: {{ variable.type }},
        {% endfor %}
        {% for variable in class_definition.variables_with_defaults %}
        {{ variable.name }}: {{ variable.type }} = {{ variable.default }},
        {% endfor %}
    ):
        # Automatically Generated

        {% for variable in class_definition.variables_without_defaults %}
        self.{{ variable.name }}: {{ variable.type }} = {{ variable.name }}
        {% endfor %}
        {% for variable in class_definition.variables_with_defaults %}
        self.{{ variable.name }}: {{ variable.type }} = {{ variable.name }}
        {% endfor %}
        pass

    {% if class_definition.variables_without_defaults|length > 0 or class_definition.variables_with_defaults|length > 0 %}
    @classmethod
    async def load(
        cls,
        key,
        conn=None,
        shallow=False
    ) -> atom.{{ class_definition.name }}:
        raise NotImplementedError

    @classmethod
    async def retrieve(
        cls,
        conn=None,
        shallow=False,
        order_by=[],
        offset=0,
        limit=None,
        *,
        instance=None,
        xid=None,
        xname=None,
        {% for variable in class_definition.variables_without_defaults %}
        {{ variable.name }}=None,
        {% endfor %}
        {% for variable in class_definition.variables_with_defaults %}
        {{ variable.name }}=None,
        {% endfor %}
    ) -> typing.List[atom.{{ class_definition.name }}]:
        raise NotImplementedError
    {% endif %}


{% endfor %}


"""
