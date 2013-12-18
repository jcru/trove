#    Copyright 2014 Rackspace Hosting
#    All Rights Reserved.
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

import uuid
import testtools
from mock import Mock
from trove.metadata.models import Metadata
from trove.metadata.service import MetadataController
from trove.metadata.views import MetadataView
from trove.tests.unittests.util import util
import time
from trove.common import context
from trove.common import wsgi

CONTEXT = context.TroveContext(tenant='TENANT-' + str(int(time.time())))


class FakeRequest(object):
    def __init__(self):
        self.__dict__[wsgi.CONTEXT_KEY] = CONTEXT

    @property
    def host(self):
        return 'service.host.com'

    @property
    def url_version(self):
        return '1.1'

    @property
    def environ(self):
        return self.__dict__


class TestMetadataBase(testtools.TestCase):
    def setUp(self):
        # Basic setup and mock/fake structures for testing only
        super(TestMetadataBase, self).setUp()
        util.init_db()
        self.metadata_key = 'replication_contract'
        self.metadata_value = {
            'replicates_from': [
                '07085bb9-59a3-40a3-9f10-dc24da644c37'
            ],
            'writeable': True
        }
        self.metadata = {
            self.metadata_key: self.metadata_value,
            'secondKey': [1, 2, {'one': 1}]
        }
        self.create_body = {
            'metadata': {
                'value': self.metadata['secondKey']
            }
        }
        self.replace_body = {
            'metadata': {
                'key': 'replication_contract',
                'value': {
                    'replicates_from': [
                        '07085bb9-59a3-40a3-9f10-dc24da644c37',
                        '4e0b99aa-43e6-4738-9263-a9d9e9ab38eb'
                    ],
                    'writeable': False
                }
            }
        }
        self.update_body = {
            'metadata': {
                'value': 'newValue'
            }
        }
        self.instance_id = str(uuid.uuid4())
        self.second_instance_id = str(uuid.uuid4())
        self.tenant_id = 'bae4c4d3-3188-4da9-9d97-d2cea9d8c062'
        self.context = CONTEXT
        self.req = FakeRequest()
        self.controller = MetadataController()
        self.serialization_type = 'application/json'
        self.dbmetadata = Metadata(self.context, self.instance_id)

        for k, v in self.metadata.iteritems():
            self.dbmetadata[k] = v

        # This helps to make sure we test the unique constraint and foreign
        # key constrain on the database model.
        self.second_dbmetadata = Metadata(self.context,
                                          self.second_instance_id)

        for k, v in self.metadata.iteritems():
            self.second_dbmetadata[k] = v

        self.metadata_view = MetadataView(self.dbmetadata, Mock()).data()

    def tearDown(self):
        super(TestMetadataBase, self).tearDown()
