from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
hz_token = Table('hz_token', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('license', String(length=140)),
    Column('token', String(length=140)),
    Column('refreshToken', String(length=140)),
    Column('expiresIn', Integer),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['hz_token'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['hz_token'].drop()
