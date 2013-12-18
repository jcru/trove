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

from mock import Mock
from trove.metadata.models import InstanceMetadata
from trove.metadata.views import MetadataView
from trove.tests.unittests.metadata.base import TestMetadataBase


class TestMetadataViews(TestMetadataBase):
    def setUp(self):
        super(TestMetadataViews, self).setUp()

    def tearDown(self):
        super(TestMetadataViews, self).tearDown()

    def test_metadata_view_instance(self):
        metadata = InstanceMetadata(self.context, self.instance_id)
        view = MetadataView(metadata, Mock())
        result = view.data()['metadata']
        for key in result:
            self.assertIn(key, self.metadata.keys())
            self.assertIn(result[key], self.metadata.values())
