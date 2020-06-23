# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import mock
from oslo_utils import importutils

from delfin import context
from delfin import exception
from delfin.tests.unit.alert_manager import fakes


class AlertProcessorTestCase(unittest.TestCase):
    ALERT_PROCESSOR_CLASS = 'delfin.alert_manager.alert_processor' \
                            '.AlertProcessor'

    def _get_alert_processor(self):
        alert_processor_class = importutils.import_class(
            self.ALERT_PROCESSOR_CLASS)
        alert_processor = alert_processor_class()
        return alert_processor

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.drivers.api.API.parse_alert')
    @mock.patch('delfin.alert_manager.alert_processor.AlertProcessor'
                '._export_alert_model')
    def test_process_alert_info_success(self, mock_export_model,
                                        mock_parse_alert, mock_storage):
        fake_storage_info = fakes.fake_storage_info()

        input_alert = {'storage_id': 'abcd-1234-56789',
                       'model': 'fake_model', 'connUnitEventId': 79,
                       'connUnitName': '000192601409',
                       'connUnitEventType': 'topology',
                       'connUnitEventDescr': 'Diagnostic '
                                             'event trace triggered.',
                       'connUnitEventSeverity': 'warning',
                       'connUnitType': 'storage-subsystem',
                       'asyncEventSource': 'eventsource1',
                       'asyncEventCode': '1050',
                       'asyncEventComponentType': '1051',
                       'asyncEventComponentName': 'comp1'}

        expected_driver_input = input_alert
        expected_driver_input['storage_name'] = fake_storage_info['name']
        expected_driver_input['vendor'] = fake_storage_info['vendor']
        expected_driver_input['model'] = fake_storage_info['model']

        expected_alert_model = {'me_dn': fake_storage_info['id'],
                                'me_name': fake_storage_info['name'],
                                'manufacturer': fake_storage_info['vendor'],
                                'location': 'Component type: location1 '
                                            'Group,Component name: comp1',
                                'event_type': input_alert['connUnitEventType'],
                                'severity':
                                    input_alert['connUnitEventSeverity'],
                                'probable_cause':
                                    input_alert['connUnitEventDescr'],
                                'me_category': input_alert['connUnitType'],
                                'native_me_dn': input_alert['connUnitName'],
                                'alarm_id': input_alert['asyncEventCode'],
                                'alarm_name':
                                    'SAMPLE_ALARM_NAME'
                                }
        mock_storage.return_value = fake_storage_info
        mock_parse_alert.return_value = fakes.fake_alert_model()
        alert_processor_inst = self._get_alert_processor()
        alert_processor_inst.process_alert_info(input_alert)

        # Verify that storage parameters correctly filled and provided as
        # input to driver
        mock_parse_alert.assert_called_once_with(context,
                                                 expected_driver_input[
                                                     'storage_id'],
                                                 expected_driver_input)

        # Verify that model returned by driver is exported
        mock_export_model.assert_called_once_with(expected_alert_model)

    @mock.patch('delfin.db.storage_get')
    @mock.patch('delfin.drivers.api.API.parse_alert',
                fakes.parse_alert_exception)
    def test_process_alert_info_exception(self, mock_storage):
        """ Mock parse alert for raising exception"""
        alert = {'storage_id': 'abcd-1234-56789',
                 'storage_name': 'storage1', 'vendor': 'fake vendor',
                 'model': 'fake model'}

        mock_storage.return_value = fakes.fake_storage_info()
        alert_processor_inst = self._get_alert_processor()
        self.assertRaisesRegex(exception.InvalidResults,
                               "Failed to fill the alert model from driver.",
                               alert_processor_inst.process_alert_info, alert)
