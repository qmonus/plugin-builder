from __future__ import annotations
from qmonus_plugin_builder.scenario_libs import component as comp
from qmonus_sdk_plugins.libs.scenario_globals import *


# Define scenario metadata (method, uri, etc.) with 'ScenarioHeader' class.
class ScenarioHeader(comp.BaseHeader):
    def __setting__(self):
        return comp.Setting(
            method="POST",
            uri="/v1/users",
            transaction=comp.Transaction(
                enable=True,
                lock_keys=[
                    'lock_keys',
                ],
            ),
        )


# Define global variables.
req: dict = comp.global_variable()
id: str = comp.global_variable()
lock_keys: list = comp.global_variable()


# Define scenario commands with 'Command{0, 1, 2, ...}' classes.
class Command0(comp.RequestValidation):
    def __setting__(self):
        return comp.RequestValidationSetting()

    def body(self):
        """body schema"""
        return {
            "type": "object",
            "required": [
                "user"
            ],
            "properties": {
                "user": {
                    "type": "object",
                    "required": [
                        "name",
                        "description"
                    ],
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        }
                    }
                }
            }
        }

    async def post_process(self):
        global req
        global id
        global lock_keys

        req = json.loads(context.session.request.body)['user']
        id = atom.User.generate_id()
        lock_keys = [id]


class Command1(comp.Script):
    def __setting__(self):
        return comp.ScriptSetting(
            label='Response'
        )

    async def code(self):
        user = atom.User(
            id=id,
            name=req['name'],
            description=req['description'],
            type=context.constants.USER_TYPE_MEMBER,
        )
        await user.save()

        res = {"user": user.to_dict()}

        context.session.set_status(201)
        context.session.finish(res)

    async def cancel_code(self):
        # Cancel
        user = await atom.User.load(id)
        if user:
            await user.destroy()
