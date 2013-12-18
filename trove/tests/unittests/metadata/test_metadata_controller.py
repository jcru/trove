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

import jsonschema
from trove.common.exception import BadRequest
from trove.common.exception import NotFound
from trove.tests.unittests.metadata.base import TestMetadataBase


class TestMetadataController(TestMetadataBase):
    def setUp(self):
        super(TestMetadataController, self).setUp()

    def tearDown(self):
        super(TestMetadataController, self).tearDown()

    def test_get_schema_create(self):
        schema = self.controller.get_schema('create', self.metadata_view)
        self.assertIsNotNone(schema)
        self.assertTrue('metadata' in schema['properties'])

    def test_get_schema_update(self):
        schema = self.controller.get_schema('update', self.metadata_view)
        self.assertIsNotNone(schema)
        self.assertTrue('metadata' in schema['properties'])

    def test_get_schema_edit(self):
        schema = self.controller.get_schema('edit', self.metadata_view)
        self.assertIsNotNone(schema)
        self.assertTrue('metadata' in schema['properties'])

    def test_validate_schema_create(self):
        body = self.create_body
        schema = self.controller.get_schema('metadata:create', body)
        validator = jsonschema.Draft4Validator(schema)
        self.assertTrue(validator.is_valid(body))

    def test_validate_schema_update(self):
        body = self.update_body
        schema = self.controller.get_schema('metadata:update', body)
        validator = jsonschema.Draft4Validator(schema)
        self.assertTrue(validator.is_valid(body))

    def test_validate_schema_edit(self):
        body = self.replace_body
        schema = self.controller.get_schema('metadata:edit', body)
        validator = jsonschema.Draft4Validator(schema)
        self.assertTrue(validator.is_valid(body))

    def test_show(self):
        result = self.controller.show(
            self.req, self.tenant_id, self.instance_id, self.metadata_key)
        self.assertEqual(
            result.data(
                self.serialization_type)['metadata'][self.metadata_key],
            self.metadata_view['metadata'][self.metadata_key])
        self.assertEqual(200, result.status)

    def test_show_noexist(self):
        self.assertRaises(NotFound, self.controller.show, self.req,
                          self.tenant_id, self.instance_id,
                          'this_key_doesnt_exist')

    def test_create(self):
        key = 'testCreateKey'
        body = {
            'metadata': {
                'value': {'two': [4, 3, 56]}
            }
        }
        result = self.controller.create(
            self.req, body, self.tenant_id, self.instance_id, key)
        self.assertEqual(200, result.status)
        result = self.controller.list(self.req, self.tenant_id,
                                      self.instance_id)
        data = result.data(self.serialization_type)
        self.assertEqual(data['metadata'][key], body['metadata']['value'])

    def test_create_already_exists(self):
        self.assertRaises(BadRequest, self.controller.create, self.req,
                          self.create_body, self.tenant_id, self.instance_id,
                          self.metadata_key)

    def test_edit(self):
        meta_to_replace = {
            'metadata': {
                'value': {
                    'replicates_from': [
                        '07085bb9-59a3-40a3-9f10-dc24da644c37'
                    ],
                    'replicates_to': [
                        'a94557b7-aef5-4c33-bcd6-adce1428351c'
                    ],
                    'writeable': True
                }
            }
        }
        result = self.controller.edit(self.req, meta_to_replace,
                                      self.tenant_id, self.instance_id,
                                      self.metadata_key)
        self.assertEqual(200, result.status)
        result = self.controller.show(self.req, self.tenant_id,
                                      self.instance_id, self.metadata_key)
        data = result.data(self.serialization_type)['metadata']
        self.assertEqual(meta_to_replace['metadata']['value'],
                         data[self.metadata_key])

    def test_edit_noexists(self):
        meta_to_replace = {
            'metadata': {
                'value': {
                    'replicates_from': [
                        '07085bb9-59a3-40a3-9f10-dc24da644c37'
                    ],
                    'replicates_to': [
                        'a94557b7-aef5-4c33-bcd6-adce1428351c'
                    ],
                    'writeable': True
                }
            }
        }
        self.assertRaises(NotFound, self.controller.edit, self.req,
                          meta_to_replace, self.tenant_id, self.instance_id,
                          'this_key_doesnt_exist')

    def test_delete(self):
        old_meta = self.controller.list(self.req, self.tenant_id,
                                        self.instance_id).data(
                                            self.serialization_type)
        result = self.controller.delete(self.req, self.tenant_id,
                                        self.instance_id, self.metadata_key)
        # test response from delete
        self.assertEqual(200, result.status)
        new_meta = self.controller.list(self.req, self.tenant_id,
                                        self.instance_id).data(
                                            self.serialization_type)
        # test response code from list
        self.assertEqual(200, result.status)
        self.assertNotEqual(old_meta, new_meta)
        self.assertNotIn(self.metadata_key, new_meta.keys())

    def test_delete_noexists(self):
        self.assertRaises(NotFound, self.controller.delete, self.req,
                          self.tenant_id, self.instance_id,
                          'this_key_doesnt_exist')

    def test_update(self):
        old_meta = self.controller.show(self.req, self.tenant_id,
                                        self.instance_id,
                                        self.metadata_key).data(
                                            self.serialization_type)
        newkey = 'newKey'
        meta_to_update = {
            'metadata': {
                'key': newkey,
                'value': {
                    'testValue': [
                        'a94557b7-aef5-4c33-bcd6-adce1428351c'
                    ],
                    'isGoodTest': True
                }
            }
        }
        result = self.controller.update(self.req, meta_to_update,
                                        self.tenant_id, self.instance_id,
                                        self.metadata_key)
        self.assertEqual(200, result.status)

        result = self.controller.show(self.req, self.tenant_id,
                                      self.instance_id, newkey)
        data = result.data(self.serialization_type)
        self.assertNotIn(self.metadata_key,
                         old_meta['metadata'][self.metadata_key])
        self.assertIn(newkey, data['metadata'].keys())
        self.assertEqual(data['metadata'][newkey],
                         meta_to_update['metadata']['value'])

    def test_update_noexists(self):
        meta_to_update = {
            'metadata': {
                'key': 'newKey',
                'value': {
                    'testValue': [
                        'a94557b7-aef5-4c33-bcd6-adce1428351c'
                    ],
                    'isGoodTest': True
                }
            }
        }
        self.assertRaises(NotFound, self.controller.update, self.req,
                          meta_to_update, self.tenant_id, self.instance_id,
                          'this_key_doesnt_exist')
