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

from delfin.api.validation import parameter_types


put = {
    'type': 'object',
    'properties': {
        'host': parameter_types.hostname_or_ip_address,
        'version': parameter_types.snmp_version,
        'community_string': {'type': 'string',
                             'minLength': 1,
                             'maxLength': 255},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'security_level': parameter_types.snmp_security_level,
        'auth_key': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'auth_protocol': parameter_types.snmp_auth_protocol,
        'privacy_protocol': parameter_types.snmp_privacy_protocol,
        'privacy_key': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'engine_id': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['host', 'version'],
    'additionalProperties': False,
}
