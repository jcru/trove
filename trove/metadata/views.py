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

from trove.openstack.common import log as logging
from trove.openstack.common.gettextutils import _

LOG = logging.getLogger(__name__)


class MetadataKeyValueView(object):
    def __init__(self, metadata, req=None):
        """
        Create a new metadata view object.

        :param metadata: Metadata SQLAlchemy model object
        :param req: wsgi.Request object

        :rtype: MetadataView
        """
        self.metadata = metadata
        self.req = req

    def data(self):
        """
        Return a properly formatted dictionary representation of a
        Metadata SQLAlchemy object.

        This returns a dictionary that is properly formatted for returning
        back to the api for manipulating the metadata for an instance.

        :rtype: dict
        """
        LOG.info(_('MetadataKeyValue %(key)s: %(value)s') %
                 {'key': self.metadata.key, 'value': self.metadata.value})
        data = {'metadata': {self.metadata.key: self.metadata.value}}
        LOG.info(_('MetadataKeyValueView returning data: %s') % data)
        return data


class MetadataView(object):
    def __init__(self, metadata, req=None):
        """
        Create a new metadata view object.

        :param metadata: Metadata SQLAlchemy model object
        :param req: wsgi.Request object

        :rtype: MetadataView
        """
        self.metadata = metadata
        self.req = req

    def data(self):
        """
        Return a properly formatted dictionary representation of a
        Metadata SQLAlchemy object.

        This returns a dictionary that is properly formatted for returning
        back to the api for manipulating the metadata for an instance.

        :rtype: dict
        """
        LOG.info(_('Metadata for instance: %s') % self.metadata)
        data = {'metadata': self.metadata.copy()}
        LOG.info(_('MetadataView returning data: %s') % data)
        return data
