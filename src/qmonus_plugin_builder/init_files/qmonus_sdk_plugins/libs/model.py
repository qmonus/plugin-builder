##########################
# Automatically generated
##########################

from qmonus_plugin_builder.sdk_libs.model import aiodb

import sqlalchemy

metadata = sqlalchemy.MetaData()


User = sqlalchemy.Table(
    "User", metadata,
    sqlalchemy.Column("name"),
    sqlalchemy.Column("description"),
    sqlalchemy.Column("type"),
    sqlalchemy.Column("id"),
    sqlalchemy.Column("instance"),
    sqlalchemy.Column("xid"),
    sqlalchemy.Column("xname"),
)

