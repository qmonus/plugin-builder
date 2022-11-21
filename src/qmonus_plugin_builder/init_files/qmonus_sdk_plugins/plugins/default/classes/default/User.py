from __future__ import annotations
from qmonus_plugin_builder.class_libs import component as comp
from qmonus_sdk_plugins.libs import classes
from qmonus_sdk_plugins.libs.class_globals import *


# Define a class.
# The filename must be '{class-name}.py'.
# Use '@classmethod' decorator to define a class method.
# Use '@comp.instance_method()' to define an instance method.
class User(classes.User):
    def __setting__(self):
        return comp.Setting(
            identifier=comp.Identifier(name='id', type=comp.STRING(), immutable=True),
            local_fields=[
                comp.LocalField(name='name', type=comp.STRING(), nullable=False),
                comp.LocalField(name='description', type=comp.STRING(), nullable=False),
                comp.LocalField(name='type', type=comp.STRING(), nullable=False),
            ],
        )

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())

    @comp.instance_method()
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
        }

    @comp.instance_method()
    async def do_something(self, region: str = options.region):
        print(region)
