from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
hz_test = Table('hz_test', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('test', VARCHAR(length=100)),
)

hz_location = Table('hz_location', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('build_id', String(length=40)),
    Column('floor_no', String(length=40)),
    Column('user_id', String(length=40)),
    Column('x', Float),
    Column('y', Float),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['hz_test'].drop()
    post_meta.tables['hz_location'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['hz_test'].create()
    post_meta.tables['hz_location'].drop()
