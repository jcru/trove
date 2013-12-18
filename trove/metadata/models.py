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

"""
Model classes that form the core of Metadata functionality
"""

import json

from trove.common import exception
from trove.db import models
from trove.openstack.common.gettextutils import _


def persisted_models():
    return {'instance_metadata': DBInstanceMetadata}


class DBInstanceMetadata(models.DatabaseModelBase):
    _data_fields = ['id', 'instance_id', 'key', 'value', 'created',
                    'updated', 'deleted', 'deleted_at']
    preserve_on_delete = False
    _table_name = 'instance_metadata'


class InstanceMetadataEntry(object):
    def __init__(self, db_instance_metadata_entry):
        """
        This represents a row in the database but wraps it in a way that
        allows the InstanceMetadata class to satisfy a dictionary interface.

        This object is meant to be used by InstanceMetadata which retrieves
        all metadata entries for a specific instance_id.
        """
        self.metadata = db_instance_metadata_entry

    def __repr__(self):
        return ('<trove.metadata.models.InstanceMetadataEntry object, %s: %s>'
                % (self.metadata.key, self.metadata.value))

    def set_value(self, new_value):
        """
        Value setter that ensures the data is synchronized to the database.

        :param new_value: Value to set in the database
        """
        self.metadata.value = json.dumps(new_value)
        self.metadata.save()

    def delete(self):
        """
        Expose the underlying SQLAlchemy result object's delete function
        """
        self.metadata.delete()

    def save(self):
        """
        Expose the underlying SQLAlchemy result object's save function
        """
        self.metadata.save()

    @property
    def key(self):
        return self.metadata.key

    @property
    def value(self):
        return json.loads(self.metadata.value)

    @property
    def id(self):
        return self.metadata.id

    def copy(self):
        return {
            self.key: self.value
        }


class InstanceMetadata(object):
    """
    Instance metadata contains all metadata entries for the specified
    instance_id.

    This object should always satisfy the dictionary
    interface to keep usage simple.
    """
    def __init__(self, context, instance_id):
        """
        Returns an InstanceMetadata object.

        :param context: TroveContext object
        :param instance_id: UUID of the instance to add/modify metadata for
        """
        if context and instance_id:
            self.context = context
            self.instance_id = instance_id
        else:
            raise exception.NotFound(
                _('Not enough given to find metadata'))

        self._load_metadata()

    def _load_metadata(self):
        """
        Helper method for refreshing metadata from the database.  This is
        called at instantiation and anytime metadata is added to the instance.
        """
        # NOTE(imsplitbit): if this becomes too expensive of an operation we
        # can break it out into 2 methods.  One for when instantiation happens
        # and one for just loading the newly created metadata entries into
        # the self.metadata list
        if self.context:
            entries = DBInstanceMetadata.find_all(
                instance_id=self.instance_id, deleted=False).all()
            self.metadata = [InstanceMetadataEntry(entry)
                             for entry in entries]

    def _create_new_db_entry(self, key, value):
        return DBInstanceMetadata.create(context=self.context,
                                         instance_id=self.instance_id,
                                         key=key,
                                         value=json.dumps(value)).save()

    def __iter__(self):
        for metadata in self.metadata:
            yield metadata.key

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, item):
        for metadata in self.metadata:
            if metadata.key == item:
                return metadata.value

    def __delitem__(self, item):
        for metadata in self.metadata:
            if metadata.key == item:
                metadata.delete()

        self._load_metadata()

    def __setitem__(self, key, value):
        # NOTE(imsplitbit): There is a known issue here where users of
        # this model will need to act upon each key/value pair in whole
        # because the metadata values are stored in marshaled form so there
        # is no way to do an operation on nested objects.

        metadata = None
        for meta in self.metadata:
            if meta.key == key:
                # The key already exists so this an update operation
                metadata = meta
                metadata.set_value(value)

        if not metadata:
            # This isn't an update operation so make a new metadata entry
            new_entry = self._create_new_db_entry(key, value)
            self.metadata.append(InstanceMetadataEntry(new_entry))

    def __contains__(self, item):
        for metadata in self.metadata:
            if metadata.key == item:
                return True

        return False

    def __eq__(self, other):
        # use self.copy() to render a dictionary and then allow python's
        # dict builtin to do the comparison.
        return self.copy() == other

    def __ne__(self, other):
        # use self.copy() to render a dictionary and then allow python's
        # dict builtin to do the comparison.
        return self.copy() != other

    def __repr__(self):
        # use self.copy() to render a dictionary and then allow python's
        # dict builtin __repr__
        return self.copy().__repr__()

    def __str__(self):
        # use self.copy() to render a dictionary and then allow python's
        # dict builtin __str__
        return self.copy().__str__()

    def keys(self):
        keys = list()
        for metadata in self.metadata:
            keys.append(metadata.key)

        return keys

    def values(self):
        values = list()

        for metadata in self.metadata:
            values.append(metadata.value)

        return values

    def items(self):
        items = list()

        for metadata in self.metadata:
            items.append((metadata.key, metadata.value))

        return items

    def get(self, key, default=None):
        value = default

        for metadata in self.metadata:
            if metadata.key == key:
                value = metadata.value

        return value

    def clear(self):
        for metadata in self.metadata:
            metadata.delete()

        self._load_metadata()

    def iterkeys(self):
        for key in self.keys():
            yield key

    def pop(self, key):
        for metadata in self.metadata:
            if metadata.key == key:
                return metadata.value

        raise KeyError(key)

    def itervalues(self):
        for value in self.values():
            yield value

    def iteritems(self):
        for item in self.items():
            yield item

    def copy(self):
        result = {}
        for metadata in self.metadata:
            result[metadata.key] = metadata.value

        return result

    def entity_for_key(self, key):
        """
        Return the InstanceMetadataEntry object for a given key should it
        exist.  This is used solely for our InstanceMetadataEntryView objects.

        :param key: Key for which we need a InstanceMetadataEntry object
        """
        for metadata in self.metadata:
            if metadata.key == key:
                return metadata
        return None
