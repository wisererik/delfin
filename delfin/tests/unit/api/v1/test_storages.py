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

from unittest import mock

from delfin.common import constants

from delfin import db
from delfin import exception
from delfin import test
from delfin.api.v1.storages import StorageController
from delfin.tests.unit.api import fakes


class TestStorageController(test.TestCase):

    def setUp(self):
        super(TestStorageController, self).setUp()
        self.task_rpcapi = mock.Mock()
        self.driver_api = mock.Mock()
        self.controller = StorageController()
        self.mock_object(self.controller, 'task_rpcapi', self.task_rpcapi)
        self.mock_object(self.controller, 'driver_api', self.driver_api)

    @mock.patch.object(db, 'storage_get',
                       mock.Mock(return_value={'id': 'fake_id'}))
    def test_delete(self):
        req = fakes.HTTPRequest.blank('/storages/fake_id')
        self.controller.delete(req, 'fake_id')
        ctxt = req.environ['delfin.context']
        db.storage_get.assert_called_once_with(ctxt, 'fake_id')
        self.task_rpcapi.remove_storage_resource.assert_called_with(
            ctxt, 'fake_id', mock.ANY)
        self.task_rpcapi.remove_storage_in_cache.assert_called_once_with(
            ctxt, 'fake_id')

    def test_delete_with_invalid_id(self):
        self.mock_object(
            db, 'storage_get',
            mock.Mock(side_effect=exception.StorageNotFound('fake_id')))
        req = fakes.HTTPRequest.blank('/storages/fake_id')
        self.assertRaises(exception.StorageNotFound,
                          self.controller.delete,
                          req, 'fake_id')

    def test_list(self):
        self.mock_object(
            db, 'storage_get_all',
            fakes.fake_storages_get_all)
        req = fakes.HTTPRequest.blank('/storages')

        res_dict = self.controller.index(req)

        expctd_dict = {
            "storages": [
                {
                    "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
                    "created_at": "2020-06-09T08:59:48.710890",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:59:48.769470",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000113",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                },
                {
                    "id": "277a1d8f-a36e-423e-bdd9-db154f32c289",
                    "created_at": "2020-06-09T08:58:23.008821",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:58:23.033601",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000112",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_list_with_filter(self):
        self.mock_object(
            db, 'storage_get_all',
            fakes.fake_storages_get_all_with_filter)
        req = fakes.HTTPRequest.blank(
            '/storages/?name=fake_driver&sort=name:asc&wrongfilter=remove')
        res_dict = self.controller.index(req)
        expctd_dict = {
            "storages": [
                {
                    "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
                    "created_at": "2020-06-09T08:59:48.710890",
                    "free_capacity": 1045449,
                    "updated_at": "2020-06-09T08:59:48.769470",
                    "name": "fake_driver",
                    "location": "HK",
                    "firmware_version": "1.0.0",
                    "vendor": "fake_vendor",
                    "status": "normal",
                    "sync_status": "SYNCED",
                    "model": "fake_model",
                    "description": "it is a fake driver.",
                    "serial_number": "2102453JPN12KA0000113",
                    "used_capacity": 3126,
                    "total_capacity": 1048576
                }
            ]
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show(self):
        self.mock_object(
            db, 'storage_get',
            fakes.fake_storages_show)
        req = fakes.HTTPRequest.blank(
            '/storages/12c2d52f-01bc-41f5-b73f-7abf6f38a2a6')

        res_dict = self.controller.show(req,
                                        '12c2d52f-01bc-41f5-b73f-7abf6f38a2a6')
        expctd_dict = {
            "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
            "created_at": "2020-06-09T08:59:48.710890",
            "free_capacity": 1045449,
            "updated_at": "2020-06-09T08:59:48.769470",
            "name": "fake_driver",
            "location": "HK",
            "firmware_version": "1.0.0",
            "vendor": "fake_vendor",
            "status": "normal",
            "sync_status": "SYNCED",
            "model": "fake_model",
            "description": "it is a fake driver.",
            "serial_number": "2102453JPN12KA0000113",
            "used_capacity": 3126,
            "total_capacity": 1048576
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_show_with_invalid_id(self):
        self.mock_object(
            db, 'storage_get',
            mock.Mock(side_effect=exception.StorageNotFound('fake_id')))
        req = fakes.HTTPRequest.blank('/storages/fake_id')
        self.assertRaises(exception.StorageNotFound,
                          self.controller.show,
                          req, 'fake_id')

    def test_create(self):
        self.mock_object(
            self.controller.driver_api, 'discover_storage',
            mock.Mock(return_value={
                "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
                'name': 'fake_driver',
                'description': 'it is a fake driver.',
                'vendor': 'fake_vendor',
                'model': 'fake_model',
                'status': 'normal',
                'serial_number': '2102453JPN12KA000011',
                'firmware_version': '1.0.0',
                'location': 'HK',
                'total_capacity': 1024 * 1024,
                'used_capacity': 3126,
                'free_capacity': 1045449,
                "sync_status": constants.SyncStatus.SYNCED,
            }))
        self.mock_object(
            db, 'access_info_get_all',
            fakes.fake_access_info_get_all)
        self.mock_object(
            db, 'storage_get',
            mock.Mock(side_effect=exception.StorageNotFound('fake_id')))
        self.mock_object(
            self.controller, 'sync',
            fakes.fake_sync)
        body = {
            'model': 'fake_driver',
            'vendor': 'fake_storage',
            'username': 'admin',
            'extra_attributes': {'array_id': '0001234567891'},
            'password': 'abcd',
            'host': '10.0.0.76',
            'port': 1234
        }
        req = fakes.HTTPRequest.blank(
            '/storages')
        res_dict = self.controller.create(req,
                                          body=body)
        expctd_dict = {
            "id": "12c2d52f-01bc-41f5-b73f-7abf6f38a2a6",
            'name': 'fake_driver',
            'description': 'it is a fake driver.',
            'vendor': 'fake_vendor',
            'model': 'fake_model',
            'status': 'normal',
            'serial_number': '2102453JPN12KA000011',
            'firmware_version': '1.0.0',
            'location': 'HK',
            'total_capacity': 1024 * 1024,
            'used_capacity': 3126,
            'free_capacity': 1045449,
            "sync_status": "SYNCED",
        }
        self.assertDictEqual(expctd_dict, res_dict)

    def test_create_when_storage_already_exists(self):
        self.mock_object(
            self.controller.driver_api, 'discover_storage',
            mock.Mock(return_value={
                "id": "5f5c806d-2e65-473c-b612-345ef43f0642",
                'name': 'fake_driver',
                'description': 'it is a fake driver.',
                'vendor': 'fake_vendor',
                'model': 'fake_model',
                'status': 'normal',
                'serial_number': '2102453JPN12KA000011',
                'firmware_version': '1.0.0',
                'location': 'HK',
                'total_capacity': 1024 * 1024,
                'used_capacity': 3126,
                'free_capacity': 1045449,
                "sync_status": constants.SyncStatus.SYNCED,
            }))
        self.mock_object(
            db, 'access_info_get_all',
            fakes.fake_access_info_get_all)
        self.mock_object(
            db, 'storage_get',
            fakes.fake_storages_show)
        self.mock_object(
            self.controller, 'sync',
            fakes.fake_sync)
        body = {
            'model': 'fake_driver',
            'vendor': 'fake_storage',
            'username': 'admin',
            'extra_attributes': {'array_id': '0001234567891'},
            'password': 'abcd',
            'host': '10.0.0.76',
            'port': 1234
        }
        req = fakes.HTTPRequest.blank(
            '/storages')
        self.assertRaises(exception.StorageAlreadyExists,
                          self.controller.create,
                          req, body=body)
