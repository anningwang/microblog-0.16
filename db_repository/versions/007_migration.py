from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
hz_token = Table('hz_token', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('license', VARCHAR(length=140)),
    Column('token', VARCHAR(length=140)),
    Column('refreshToken', VARCHAR(length=140)),
    Column('expiresIn', INTEGER),
    Column('timestamp', DATETIME),
)

hz_token = Table('hz_token', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('license', String(length=140)),
    Column('token', String(length=140)),
    Column('refresh_token', String(length=140)),
    Column('expires_in', Integer),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['hz_token'].columns['expiresIn'].drop()
    pre_meta.tables['hz_token'].columns['refreshToken'].drop()
    post_meta.tables['hz_token'].columns['expires_in'].create()
    post_meta.tables['hz_token'].columns['refresh_token'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['hz_token'].columns['expiresIn'].create()
    pre_meta.tables['hz_token'].columns['refreshToken'].create()
    post_meta.tables['hz_token'].columns['expires_in'].drop()
    post_meta.tables['hz_token'].columns['refresh_token'].drop()
