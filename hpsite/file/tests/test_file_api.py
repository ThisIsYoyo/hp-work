import json
import os
import shutil
from pathlib import Path
from django.test import TestCase
from rest_framework import status

PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.parent


class TestFileApi(TestCase):
    TEST_DIR = 'hpsite/file/tests/test_dir'
    TEST_FILE_NAME_CONTENT_MAP = {
        'test_path_1': 'test',
        'test_path_2': 'test, test',
        'test_path_3': 'test, test, test',
    }

    def setUp(self) -> None:
        os.mkdir(PROJECT_ROOT_PATH / self.TEST_DIR)

        for test_name_path, test_file_content in self.TEST_FILE_NAME_CONTENT_MAP.items():
            with open(PROJECT_ROOT_PATH / self.TEST_DIR / test_name_path, 'w') as fp:
                fp.write(test_file_content)

    def test_file__GET__is_file(self):
        # arrange
        file_name = list(self.TEST_FILE_NAME_CONTENT_MAP.keys())[0]
        expect_content = self.TEST_FILE_NAME_CONTENT_MAP[file_name]

        # action
        response = self.client.get(f'/file/{self.TEST_DIR}/{file_name}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.getvalue().decode('ascii'), expect_content)

    def test_file__GET__is_dir(self):
        # arrange
        expect_content = {
            'isDirectory': True,
            'files': list(self.TEST_FILE_NAME_CONTENT_MAP.keys()),
        }

        # action
        response = self.client.get(f'/file/{self.TEST_DIR}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content.decode('ascii')), expect_content)

    def test_file__GET__not_exist(self):
        # arrange
        file_name = 'not_test_file'

        # action
        response = self.client.get(f'/file/{self.TEST_DIR}/{file_name}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_file__POST__create_success(self):
        # arrange
        file_name = 'test_path_4'
        file_content = 'test four'

        # action
        response = self.client.post(f'/file/{self.TEST_DIR}/{file_name}/', data={'file': file_content})

        # assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.isfile(PROJECT_ROOT_PATH / self.TEST_DIR / file_name))

        with open(PROJECT_ROOT_PATH / self.TEST_DIR / file_name, 'r') as fp:
            actual_content = fp.read()
        self.assertEqual(actual_content, file_content)

    def test_file__POST__create_fail(self):
        # arrange
        file_name = 'test_path_3'
        file_content = 'test four'

        # action
        response = self.client.post(f'/file/{self.TEST_DIR}/{file_name}/', data={'file': file_content})

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with open(PROJECT_ROOT_PATH / self.TEST_DIR / file_name, 'r') as fp:
            actual_content = fp.read()
        self.assertNotEqual(actual_content, file_content)

    def test_file__PATCH__success(self):
        # arrange
        file_name = 'test_path_3'
        file_content = 'test four'

        # action
        response = self.client.patch(
            f'/file/{self.TEST_DIR}/{file_name}/',
            data=json.dumps({'file': file_content}),
            content_type='application/json',
        )

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with open(PROJECT_ROOT_PATH / self.TEST_DIR / file_name, 'r') as fp:
            actual_content = fp.read()
        self.assertEqual(actual_content, file_content)

    def test_file__PATCH__fail(self):
        # arrange
        file_name = 'test_path_4'
        file_content = 'test four'

        # action
        response = self.client.patch(
            f'/file/{self.TEST_DIR}/{file_name}/',
            data=json.dumps({'file': file_content}),
            content_type='application/json',
        )

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(os.path.isfile(PROJECT_ROOT_PATH / self.TEST_DIR / file_name))

    def test_file__DELETE__success(self):
        # arrange
        file_name = 'test_path_3'

        # action
        response = self.client.delete(f'/file/{self.TEST_DIR}/{file_name}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(os.path.isfile(PROJECT_ROOT_PATH / self.TEST_DIR / file_name))

    def test_file__DELETE__fail(self):
        # arrange
        file_name = 'test_path_4'

        # action
        response = self.client.delete(f'/file/{self.TEST_DIR}/{file_name}/')

        # assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self) -> None:
        shutil.rmtree(PROJECT_ROOT_PATH / self.TEST_DIR)
