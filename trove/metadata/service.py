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

from trove.common import apischema
from trove.common import exception
from trove.common import wsgi
from trove.instance import models as instances_models
from trove.metadata.models import InstanceMetadata
from trove.metadata import views
from trove.openstack.common import log as logging
from trove.openstack.common.gettextutils import _

LOG = logging.getLogger(__name__)


class MetadataController(wsgi.Controller):
    schemas = apischema.metadata.copy()

    @staticmethod
    def list(req, tenant_id, instance_id):
        """
        Show all metadata for instance {instance_id}

        :param req: wsgi.Request object
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance

        :rtype: wsgi.Result
        """
        LOG.debug(
            _('Beginning list of instance metadata for %s.') % instance_id)
        context = req.environ[wsgi.CONTEXT_KEY]
        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)
        dbmeta = InstanceMetadata(context, instance_id)
        LOG.debug(_('Finished list of instance metadata for %s.') %
                  instance_id)
        return wsgi.Result(views.MetadataView(dbmeta, req=req).data(), 200)

    @staticmethod
    def show(req, tenant_id, instance_id, key):
        """
        Show metadata for instance {instance_id}

        :param req: wsgi.Request object
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance
        :param key: key of the metadata entry

        :rtype: wsgi.Result
        """
        LOG.debug(_('Beginning show metadata key %(key)s for '
                  'instance %(instance_id)s.') %
                  {'key': key, 'instance_id': instance_id})
        context = req.environ[wsgi.CONTEXT_KEY]
        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)
        dbmeta = InstanceMetadata(context, instance_id)
        if dbmeta.get(key):
            LOG.info(_('Showing metadata key %s.') % key)
            metadata = dbmeta.entity_for_key(key)
            return wsgi.Result(
                views.MetadataKeyValueView(metadata, req=req).data(), 200)
        else:
            msg = _('No metadata key %(key)s found for instance id '
                    '%(inst_id)s.') % {'key': key, 'inst_id': instance_id}
            raise exception.NotFound(msg)

    @staticmethod
    def create(req, body, tenant_id, instance_id, key):
        """
        Create new metadata for instance {instance_id}

        body example:
        {
            'metadata': {
                'value': {'foo': ['bar', 'baz', 2]}
            }
        }

        :param req: wsgi.Request object
        :param body: Dict deserialized from the user supplied JSON
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance
        :param key: key to insert into the database

        :rtype: wsgi.Result
        """
        LOG.debug(_('Beginning create metadata key %(key)s '
                  'for instance: %(instance_id)s.') %
                  {'key': key, 'instance_id': instance_id})
        value = body['metadata']['value']
        context = req.environ[wsgi.CONTEXT_KEY]

        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)

        dbmeta = InstanceMetadata(context, instance_id)
        result = dbmeta.get(key)
        LOG.debug(_('DBmetadata result: %s.') % result)

        if not result:
            LOG.info(_('Creating key: %(key)s, value: %(value)s.') %
                     {'key': key, 'value': value})
            dbmeta[key] = value
            metadata = dbmeta.entity_for_key(key)
            LOG.debug(_('Returned result from metadata lookup: %s.') %
                      metadata)
            return wsgi.Result(
                views.MetadataKeyValueView(metadata, req).data(), 200)
        else:
            metadata = dbmeta.entity_for_key(key)
            LOG.error(_('Returned result from metadata lookup: %s.') %
                      metadata)
            raise exception.BadRequest(_('Key: %s already exists.') % key)

    @staticmethod
    def edit(req, body, tenant_id, instance_id, key):
        """
        Edit metadata value for instance {id} and {key}.  This replaces
        values of keys that are already present.

        body example:
        {
            'metadata': {
                'value': {'foo': {'bar': [2,4,3]}}
            }
        }

        :param req: wsgi.Request object
        :param body: Dict deserialized from the user supplied JSON
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance
        :param key: key for the metadata entry

        :rtype: wsgi.Result
        """
        LOG.debug(_('Beginning edit metadata key %(key)s '
                  'for instance: %(instance_id)s.') %
                  {'key': key, 'instance_id': instance_id})
        context = req.environ[wsgi.CONTEXT_KEY]

        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)

        value = body['metadata']['value']
        dbmeta = InstanceMetadata(context, instance_id)
        if key in dbmeta:
            LOG.info(_('Editing value: %(old_value)s with '
                       'value: %(new_value)s for key: %(key)s.') %
                     {'old_value': dbmeta[key], 'new_value': value,
                      'key': key})
            dbmeta[key] = value
            return wsgi.Result(None, 200)
        else:
            msg = _('Key: %s not found in database, edit impossible') % key
            raise exception.NotFound(msg)

    @staticmethod
    def update(req, body, tenant_id, instance_id, key):
        """
        Update metadata for instance {id}.  This will remove any key from
        the database that are present in the database but are not submitted in
        the body of the request.  This will also update the values of keys that
        were present.

        body example:
        {
            'metadata': {
                'key": 'newKey',
                'value': 'foo'
            }
        }

        :param req: wsgi.Request object
        :param body: Dict deserialized from the user supplied JSON
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance

        :rtype: wsgi.Result
        """
        LOG.debug(_('Beginning update metadata key %(key)s '
                  'for instance: %(instance_id)s.') %
                  {'key': key, 'instance_id': instance_id})
        context = req.environ[wsgi.CONTEXT_KEY]

        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)

        value = body['metadata']['value']
        new_key = body['metadata']['key']
        dbmeta = InstanceMetadata(context, instance_id)
        old_key = dbmeta.get(key)
        if old_key:
            LOG.info(_('Updating %(old_key)s: %(old_value)s '
                       'with %(new_key)s: %(new_value)s.') %
                     {'old_key': old_key, 'old_value': dbmeta[old_key],
                      'new_key': key, 'new_value': value})
            del(dbmeta[key])
            dbmeta[new_key] = value
            return wsgi.Result(None, 200)
        else:
            msg = (_('Metadata key: %s could not be found in the database.') %
                   key)
            raise exception.NotFound(msg)

    @staticmethod
    def delete(req, tenant_id, instance_id, key):
        """
        Delete all metadata for instance {id}

        :param req: wsgi.Request object
        :param tenant_id: Id of the tenant
        :param instance_id: UUID for the instance
        :param key: key of the metadata entry

        :rtype: wsgi.Result
        """
        LOG.debug(_('Beginning deletion of metadata key %(key)s for '
                  'instance: %(instance_id)s.') %
                  {'key': key, 'instance_id': instance_id})
        context = req.environ[wsgi.CONTEXT_KEY]

        # see if instance id being used is valid
        try:
            instances_models.get_db_info(context, instance_id)
        except exception.NotFound:
            raise exception.BadRequest(_('Instance ID: %s not valid.') %
                                       instance_id)

        dbmeta = InstanceMetadata(context, instance_id)
        if dbmeta.get(key):
            LOG.info(_('Deleting metadata key: %(key)s for instance '
                       '%(instance_id)s.') %
                     {'key': key, 'instance_id': instance_id})
            del(dbmeta[key])
            return wsgi.Result(None, 200)
        else:
            msg = _('Metadata key: %s not present in the database.') % key
            raise exception.NotFound(msg)
