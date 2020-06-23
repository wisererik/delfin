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


from unittest import TestCase, mock
from delfin import exception
from delfin import context
from delfin.drivers.dell_emc.vmax.vmax import VMAXStorageDriver


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


VMAX_STORAGE_CONF = {
    "storage_id": "12345",
    "host": "10.0.0.1",
    "port": "8443",
    "username": "user",
    "password": "pass",
    "vendor": "dell_emc",
    "model": "vmax",
    "extra_attributes": {
        "array_id": "00112233"
    }
}


class TestVMAXStorageDriver(TestCase):

    def test_init(self):
        kwargs = VMAX_STORAGE_CONF

        with mock.patch('PyU4V.U4VConn',
                        side_effect=exception.StorageBackendException):
            with self.assertRaises(Exception) as exc:
                VMAXStorageDriver(**kwargs)
            self.assertIn('Failed to connect to VMAX', str(exc.exception))

        with mock.patch('PyU4V.U4VConn', return_value=''):
            driver = VMAXStorageDriver(**kwargs)
            self.assertEqual(driver.storage_id, "12345")
            self.assertEqual(driver.client.array_id, "00112233")

        invalid_input = {'extra_attributes': {}}
        with self.assertRaises(Exception) as exc:
            VMAXStorageDriver(**invalid_input)
        self.assertIn('Input array_id is missing', str(exc.exception))

    def test_get_storage(self):
        expected = {
            'name': '',
            'vendor': 'Dell EMC',
            'description': '',
            'model': 'VMAX250F',
            'status': 'normal',
            'serial_number': '00112233',
            'location': '',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400
        }
        kwargs = VMAX_STORAGE_CONF

        m = mock.MagicMock()
        with mock.patch('PyU4V.U4VConn', return_value=m):
            driver = VMAXStorageDriver(**kwargs)
            self.assertEqual(driver.storage_id, "12345")
            self.assertEqual(driver.client.array_id, "00112233")
            model = {
                'symmetrix': [
                    {'model': 'VMAX250F'}
                ],
                'system_capacity': {
                    'usable_total_tb': 100,
                    'usable_used_tb': 75
                }
            }
            m.common.get_request.side_effect = \
                [
                    model, model,
                    model, exception.StorageBackendException,
                    exception.StorageBackendException, model]
            ret = driver.get_storage(context)
            self.assertDictEqual(ret, expected)

            with self.assertRaises(Exception) as exc:
                driver.get_storage(context)

            self.assertIn('Failed to get capacity from VMAX',
                          str(exc.exception))

            with self.assertRaises(Exception) as exc:
                driver.get_storage(context)

            self.assertIn('Failed to get model from VMAX',
                          str(exc.exception))

    def test_list_storage_pools(self):
        expected = [{
            'name': 'SRP_1',
            'storage_id': '12345',
            'native_storage_pool_id': 'SRP_ID',
            'description': 'Dell EMC VMAX Pool',
            'status': 'normal',
            'storage_type': 'block',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400
        }]
        kwargs = VMAX_STORAGE_CONF

        m = mock.MagicMock()
        with mock.patch('PyU4V.U4VConn', return_value=m):
            driver = VMAXStorageDriver(**kwargs)
            self.assertEqual(driver.storage_id, "12345")
            self.assertEqual(driver.client.array_id, "00112233")
            pool_info = {
                'srp_capacity': {
                    'usable_total_tb': 100,
                    'usable_used_tb': 75
                },
                'srpId': 'SRP_ID'
            }
            m.provisioning.get_srp_list.side_effect = \
                [['SRP_1'], ['SRP_2'], exception.StorageBackendException]
            m.provisioning.get_srp.side_effect = \
                [pool_info, exception.StorageBackendException, pool_info]
            ret = driver.list_storage_pools(context)
            self.assertDictEqual(ret[0], expected[0])

            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)

            self.assertIn('Failed to get pool metrics from VMAX',
                          str(exc.exception))

            with self.assertRaises(Exception) as exc:
                driver.list_storage_pools(context)

            self.assertIn('Failed to get pool metrics from VMAX',
                          str(exc.exception))

    def test_list_volumes(self):
        expected = [{
            'name': 'volume_1',
            'storage_id': '12345',
            'description': "Dell EMC VMAX 'thin device' volume",
            'type': 'thin',
            'status': 'available',
            'native_volume_id': '00001',
            'wwn': 'wwn123',
            'total_capacity': 104857600,
            'used_capacity': 10485760,
            'free_capacity': 94371840,
            'native_storage_pool_id': 'SRP_1',
            'compressed': True
        }]
        kwargs = VMAX_STORAGE_CONF

        m = mock.MagicMock()
        with mock.patch('PyU4V.U4VConn', return_value=m):
            driver = VMAXStorageDriver(**kwargs)
            self.assertEqual(driver.storage_id, "12345")
            self.assertEqual(driver.client.array_id, "00112233")
            volumes = {
                'volumeId': '00001',
                'cap_mb': 100,
                'allocated_percent': 10,
                'status': 'Ready',
                'type': 'TDEV',
                'wwn': 'wwn123',
                'num_of_storage_groups': 1,
                'storageGroupId': ['SG_001']
            }
            storage_group_info = {
                'srp': 'SRP_1',
                'compression': True
            }
            m.provisioning.get_volume_list.side_effect = \
                [['volume_1'], ['volume_1'],
                 exception.StorageBackendException, ['volume_1']]
            m.provisioning.get_volume.side_effect = \
                [volumes, exception.StorageBackendException,
                 volumes, volumes]
            m.provisioning.get_storage_group.side_effect = \
                [exception.StorageBackendException, storage_group_info,
                 storage_group_info, storage_group_info]

            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)

            self.assertIn('Failed to get list volumes from VMAX',
                          str(exc.exception))

            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)

            self.assertIn('Failed to get list volumes from VMAX',
                          str(exc.exception))

            with self.assertRaises(Exception) as exc:
                driver.list_volumes(context)

            self.assertIn('Failed to get list volumes from VMAX',
                          str(exc.exception))

            ret = driver.list_volumes(context)
            self.assertDictEqual(ret[0], expected[0])

    def test_delete(self):
        kwargs = VMAX_STORAGE_CONF

        m = mock.MagicMock()
        with mock.patch('PyU4V.U4VConn', return_value=m):
            driver = VMAXStorageDriver(**kwargs)
            self.assertEqual(driver.storage_id, "12345")
            self.assertEqual(driver.client.array_id, "00112233")

            m.close_session.side_effect = [
                None
            ]

            del driver
            m.close_session.assert_called()
