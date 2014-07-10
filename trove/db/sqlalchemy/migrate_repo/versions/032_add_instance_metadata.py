# Copyright 2014 Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy.schema import Column
from sqlalchemy.schema import MetaData
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.schema import ForeignKey

from trove.db.sqlalchemy.migrate_repo.schema import Boolean
from trove.db.sqlalchemy.migrate_repo.schema import DateTime
from trove.db.sqlalchemy.migrate_repo.schema import create_tables
from trove.db.sqlalchemy.migrate_repo.schema import drop_tables
from trove.db.sqlalchemy.migrate_repo.schema import String
from trove.db.sqlalchemy.migrate_repo.schema import Table
from trove.db.sqlalchemy.migrate_repo.schema import Text

meta = MetaData()

instance_metadata = Table(
    'instance_metadata',
    meta,
    Column('instance_id', String(36), ForeignKey('instances.id'),
           nullable=False),
    Column('key', String(255), nullable=False),
    Column('value', Text(), nullable=False),
    Column('created', DateTime()),
    Column('updated', DateTime()),
    Column('deleted', Boolean(), nullable=False),
    Column('deleted_at', DateTime()),
    PrimaryKeyConstraint('instance_id', 'key', name='pk_id_key')
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    Table('instances', meta, autoload=True)
    create_tables([instance_metadata])


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    drop_tables([instance_metadata])
