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


GROUP = 'dbaas.api.instances.metadata'
GROUP_CREATE = 'dbaas.api.instances.metadata.create'
GROUP_UPDATE = 'dbaas.api.instances.metadata.update'
GROUP_REPLACE = 'dbaas.api.instances.metadata.replace'
GROUP_DELETE = 'dbaas.api.instances.metadata.delete'
GROUP_LIST = 'dbaas.api.instances.metadata.list'
GROUP_SHOW = 'dbaas.api.instances.metadata.show'

from proboscis import after_class
from proboscis import before_class
from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_true
from proboscis.asserts import assert_raises

from trove.common.utils import poll_until
from trove.tests.config import CONFIG
from trove.tests.util import create_dbaas_client
from trove.tests.util.users import Requirements
from trove.tests.util import test_config

from troveclient.compat import exceptions as client_exception

FAKE = test_config.values['fake_mode']


@test(groups=[GROUP])
class TestMetadata(object):

    @before_class
    def setUp(self):
        reqs = Requirements(is_admin=False)
        self.user = CONFIG.users.find_user(reqs)
        self.dbaas = create_dbaas_client(self.user)

        self.meta_key = 'testKey'
        self.meta_value = {'one': [2, 3, 5]}
        self.new_meta_key = 'newKey'
        self.new_meta_value = {'testing': {'one': [1, 2, 3]}}

        # create an instance for running metadata tests against.
        response = self.dbaas.instances.create('metadata_test', 1,
                                               {'size': 1}, [])

        poll_until(lambda: self.dbaas.instances.get(response.id),
                   lambda instance: instance.status == 'ACTIVE',
                   sleep_time=1, time_out=120)

        self.instance = self.dbaas.instances.get(response.id)

    @after_class
    def tearDown(self):
        self.dbaas.instances.delete(self.instance.id)

    @test(groups=[GROUP, GROUP_CREATE])
    def test_metadata_create(self):
        self.dbaas.metadata.create(
            self.instance.id, self.meta_key, self.meta_value)
        resp = self.dbaas.metadata.show(self.instance.id, self.meta_key)
        assert_true(self.meta_key in resp)
        assert_equal(resp[self.meta_key], self.meta_value,
                     'Metadata did not create properly')

    @test(groups=[GROUP, GROUP_CREATE],
          depends_on=[test_metadata_create])
    def test_metadata_create_key_already_exists(self):
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.create,
                      self.instance.id, self.meta_key,
                      'this is an ambiguous value')

    def test_metadata_create_invalid_instance_id(self):
        bad_instance_id = "999"
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.create,
                      bad_instance_id, self.meta_key,
                      'this is an ambiguous value')

    @test(groups=[GROUP, GROUP_LIST], depends_on_groups=[GROUP_CREATE])
    def test_metadata_list(self):
        resp = self.dbaas.metadata.list(self.instance.id)
        assert_equal(resp[self.meta_key], self.meta_value,
                     'Unable to find key in metadata')

    @test(groups=[GROUP, GROUP_SHOW], depends_on_groups=[GROUP_CREATE])
    def test_metadata_show(self):
        resp = self.dbaas.metadata.show(self.instance.id, self.meta_key)
        assert_equal(resp[self.meta_key], self.meta_value,
                     'Metadata key could not be found')

    @test(groups=[GROUP, GROUP_SHOW], depends_on_groups=[GROUP_CREATE])
    def test_metadata_show_key_noexist(self):
        assert_raises(client_exception.NotFound, self.dbaas.metadata.show,
                      self.instance.id, 'thiskeydoesntexist')

    @test(groups=[GROUP, GROUP_SHOW], depends_on_groups=[GROUP_CREATE])
    def test_metadata_show_invalid_instance_id(self):
        bad_instance_id = "999"
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.show,
                      bad_instance_id, self.meta_key)

    @test(groups=[GROUP, GROUP_REPLACE],
          depends_on_groups=[GROUP_CREATE, GROUP_LIST, GROUP_SHOW])
    def test_metadata_edit(self):
        self.dbaas.metadata.edit(self.instance.id, self.meta_key,
                                 self.new_meta_value)
        resp = self.dbaas.metadata.show(self.instance.id, self.meta_key)
        assert_equal(resp[self.meta_key], self.new_meta_value,
                     'Replacing metadata value failed')

    @test(groups=[GROUP, GROUP_REPLACE], depends_on_groups=[GROUP_CREATE])
    def test_metadata_edit_key_noexist(self):
        assert_raises(client_exception.NotFound, self.dbaas.metadata.edit,
                      self.instance.id, 'keynoexist', self.new_meta_value)

    @test(groups=[GROUP, GROUP_REPLACE], depends_on_groups=[GROUP_CREATE])
    def test_metadata_edit_invalid_instance_id(self):
        bad_instance_id = "999"
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.edit,
                      bad_instance_id, self.meta_key, self.new_meta_value)

    @test(groups=[GROUP, GROUP_UPDATE], depends_on_groups=[GROUP_REPLACE])
    def test_metadata_update(self):
        self.dbaas.metadata.update(self.instance.id, self.meta_key,
                                   self.new_meta_key, self.new_meta_value)
        resp = self.dbaas.metadata.show(self.instance.id, self.new_meta_key)
        assert_equal(resp[self.new_meta_key], self.new_meta_value,
                     'Metadata update failed')

    @test(groups=[GROUP, GROUP_UPDATE], depends_on_groups=[GROUP_CREATE])
    def test_metadata_update_key_noexist(self):
        assert_raises(client_exception.NotFound, self.dbaas.metadata.update,
                      self.instance.id, 'keynoexist', self.new_meta_key,
                      self.new_meta_value)

    @test(groups=[GROUP, GROUP_UPDATE], depends_on_groups=[GROUP_CREATE])
    def test_metadata_update_invalid_instance_id(self):
        bad_instance_id = "999"
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.update,
                      bad_instance_id, self.meta_key, self.new_meta_key,
                      self.new_meta_value)

    @test(groups=[GROUP, GROUP_DELETE],
          depends_on_groups=[GROUP_REPLACE, GROUP_UPDATE])
    def test_metadata_delete(self):
        self.dbaas.metadata.delete(self.instance.id, self.new_meta_key)
        resp = self.dbaas.metadata.list(self.instance.id)
        assert_true(self.new_meta_key not in resp)

    @test(groups=[GROUP, GROUP_DELETE])
    def test_metadata_delete_key_noexist(self):
        assert_raises(client_exception.NotFound, self.dbaas.metadata.delete,
                      self.instance.id, 'keynoexist')

    @test(groups=[GROUP, GROUP_DELETE])
    def test_metadata_delete_invalid_instance_id(self):
        bad_instance_id = "999"
        assert_raises(client_exception.BadRequest, self.dbaas.metadata.delete,
                      bad_instance_id, self.new_meta_key)
