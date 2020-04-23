# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import six
import abc


@six.add_metaclass(abc.ABCMeta)
class StorageDriver(object):

    def __init__(self, storage_id):
        self.storage_id = storage_id

    @staticmethod
    def get_storage_registry():
        """Show register parameters which the driver needs."""
        pass

    @abc.abstractmethod
    def register_storage(self, context, register_info):
        """Discovery a storage system with register parameters."""
        pass

    @abc.abstractmethod
    def get_storage(self, context):
        """Get storage device information from storage system"""
        pass

    @abc.abstractmethod
    def list_pools(self, context):
        """List all storage pools from storage system."""
        pass

    @abc.abstractmethod
    def list_volumes(self, context):
        """List all storage volumes from storage system."""
        pass

    @abc.abstractmethod
    def parse_alert(self, context, alert):
        """Parse alert data got from snmp trap server."""
        pass

    @abc.abstractmethod
    def clear_alert(self, context, alert):
        """Clear alert from storage system."""
        pass
