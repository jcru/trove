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

from trove.common.exception import NotFound
from trove.metadata.models import InstanceMetadata
from trove.tests.unittests.metadata.base import TestMetadataBase


class TestMetadataModel(TestMetadataBase):
    def setUp(self):
        super(TestMetadataModel, self).setUp()

    def tearDown(self):
        super(TestMetadataModel, self).tearDown()

    def test_metadata__getitem__(self):
        self.assertEqual(
            self.dbmetadata['replication_contract'],
            self.metadata['replication_contract'])

    def test_metadata_keys(self):
        self.assertIn('replication_contract', self.dbmetadata.keys())

    def test_metadata_values(self):
        self.assertIn(
            self.metadata['replication_contract'], self.dbmetadata.values())

    def test_metadata__iter__(self):
        for meta in self.dbmetadata:
            self.assertIn(meta, self.metadata.keys())

    def test_metadata__eq__(self):
        self.assertTrue(self.dbmetadata == self.metadata)

    def test_metadata__ne__(self):
        self.assertFalse(self.dbmetadata != self.metadata)

    def test_metadata_len(self):
        self.assertEqual(len(self.dbmetadata), len(self.metadata))

    def test_metadata_delete(self):
        del(self.dbmetadata['replication_contract'])
        self.assertNotIn('replication_contract', self.dbmetadata.keys())

    def test_metadata_copy(self):
        metadata_copy = self.dbmetadata.copy()
        for key in metadata_copy.keys():
            self.assertIn(key, self.metadata.keys())
            self.assertIn(metadata_copy[key], self.metadata.values())

    def test_metadata_iteritems(self):
        for k, v in self.dbmetadata.iteritems():
            self.assertIn(k, self.metadata.keys())
            self.assertEqual(self.metadata[k], v)

    def test_metadata_itervalues(self):
        for v in self.dbmetadata.itervalues():
            self.assertIn(v, self.metadata.values())

    def test_metadata_iterkeys(self):
        for k in self.dbmetadata.iterkeys():
            self.assertIn(k, self.metadata.keys())

    def test_metadata_pop(self):
        key = 'replication_contract'
        data = self.dbmetadata.pop(key)
        self.assertEqual(data, self.metadata[key])

    def test_metadata_pop_no_key(self):
        key = 'this_key_doesnt_exist'
        self.assertRaises(KeyError, self.dbmetadata.pop, key)

    def test_metadata_items(self):
        for k, v in self.dbmetadata.items():
            self.assertIn(k, self.metadata.keys())
            self.assertIn(v, self.metadata.values())

    def test_metadata_get(self):
        key = 'replication_contract'
        data = self.dbmetadata.get(key)
        self.assertEqual(self.metadata[key], data)

    def test_metadata_get_default(self):
        key = 'this_key_doesnt_exist'
        default = 'this_is_the_default_value'
        data = self.dbmetadata.get(key, default)
        self.assertEqual(default, data)

    def test_metadata_get_default_none(self):
        key = 'this_key_doesnt_exist'
        data = self.dbmetadata.get(key)
        self.assertIsNone(data)

    def test_metadata_in(self):
        key = 'replication_contract'
        self.assertIn(key, self.dbmetadata)

    def test_metadata_not_in(self):
        key = 'this_key_doesnt_exist'
        self.assertNotIn(key, self.dbmetadata)

    def test_metadata_clear(self):
        self.dbmetadata.clear()
        self.assertEqual(0, len(self.dbmetadata))

    def test_metadata_copy_type(self):
        self.dbmetadata.clear()
        meta_copy = self.dbmetadata.copy()
        self.assertIsInstance(meta_copy, dict)

    def test_metadata_create_by_key_value(self):
        key = 'myNewKey'
        newmeta = {key: 'myTestValue'}
        self.dbmetadata[key] = newmeta[key]
        result = self.dbmetadata.entity_for_key(key)
        self.assertIn(key, self.dbmetadata.keys())
        self.assertEqual(newmeta, result.copy())

    def test_metadata_failed_init(self):
        self.assertRaises(NotFound, InstanceMetadata, None, None)

    def test_metadata_entity_for_key_noexist(self):
        self.assertIsNone(
            self.dbmetadata.entity_for_key('this_key_doesnt_exist'))
