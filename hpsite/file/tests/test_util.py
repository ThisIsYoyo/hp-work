import os
import shutil
from pathlib import Path
from unittest import TestCase

from file.views import filter_file_under_path, File, sort_file_list
from file.define import FileAttr, OrderDirection


class TestFileViewUtil(TestCase):
    PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent.parent

    TEST_DIR = 'hpsite/file/tests/test_dir'
    TEST_SORT_NAME_FILE_NAME_LIST = ['test_name_a', 'test_name_b', 'test_name_c']
    TEST_SORT_LAST_MODIFIED_FILE_NAME_LIST = [
        'test_last_modified_first_mod', 'test_last_modified_second_mod', 'test_last_modified_third_mod'
    ]
    TEST_SORT_SIZE_FILE_NAME_CONTENT_MAP = {
        'test_size_small': 'test',
        'test_size_medium': 'test, test',
        'test_size_large': 'test, test, test',
    }

    @classmethod
    def setUpClass(cls) -> None:
        os.mkdir(cls.PROJECT_ROOT_PATH / cls.TEST_DIR)

        for test_file_name in cls.TEST_SORT_NAME_FILE_NAME_LIST:
            with open(cls.PROJECT_ROOT_PATH / cls.TEST_DIR / test_file_name, 'w') as _:
                pass

        for test_file_name in cls.TEST_SORT_LAST_MODIFIED_FILE_NAME_LIST:
            with open(cls.PROJECT_ROOT_PATH / cls.TEST_DIR / test_file_name, 'w') as _:
                pass

        for test_file_name, test_file_content in cls.TEST_SORT_SIZE_FILE_NAME_CONTENT_MAP.items():
            with open(cls.PROJECT_ROOT_PATH / cls.TEST_DIR / test_file_name, 'w') as fp:
                fp.write(test_file_content)

    def test_filter_file_under_path__filter_empty(self):
        # arrange
        expect_file_len = (
                len(self.TEST_SORT_NAME_FILE_NAME_LIST) +
                len(self.TEST_SORT_LAST_MODIFIED_FILE_NAME_LIST) +
                len(self.TEST_SORT_SIZE_FILE_NAME_CONTENT_MAP)
        )
        expect_file_name_list = (
                self.TEST_SORT_NAME_FILE_NAME_LIST +
                self.TEST_SORT_LAST_MODIFIED_FILE_NAME_LIST +
                list(self.TEST_SORT_SIZE_FILE_NAME_CONTENT_MAP.keys())
        )

        # action
        file_list = filter_file_under_path(path=self.PROJECT_ROOT_PATH / self.TEST_DIR, filter_name='')

        # assert
        self.assertEqual(len(file_list), expect_file_len)
        self.assertEqual(set([file.name for file in file_list]), set(expect_file_name_list))

    def test_filter_file_under_path__filter_1(self):
        # arrange
        filter_name = 'test_name'
        expect_file_len = len(self.TEST_SORT_NAME_FILE_NAME_LIST)
        expect_file_name_list = self.TEST_SORT_NAME_FILE_NAME_LIST

        # action
        file_list = filter_file_under_path(path=self.PROJECT_ROOT_PATH / self.TEST_DIR, filter_name=filter_name)

        # assert
        self.assertEqual(len(file_list), expect_file_len)
        self.assertEqual([file.name for file in file_list], expect_file_name_list)

    def _prepare_sort_name_file_list(self) -> list[File]:
        return [
            File(
                last_modify_time=os.path.getmtime(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                size=os.path.getsize(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                name=file_name,
            )
            for file_name in self.TEST_SORT_NAME_FILE_NAME_LIST
        ]

    def test_sort_file_list__name__ascending(self):
        # arrange
        file_list = self._prepare_sort_name_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.NAME.value, sort_dir=OrderDirection.ASCENDING.value)

        # assert
        self.assertEqual([file.name for file in file_list], ['test_name_a', 'test_name_b', 'test_name_c'])

    def test_sort_file_list__name__descending(self):
        # arrange
        file_list = self._prepare_sort_name_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.NAME.value, sort_dir=OrderDirection.DESCENDING.value)

        # assert
        self.assertEqual([file.name for file in file_list], ['test_name_c', 'test_name_b', 'test_name_a'])

    def _prepare_sort_last_modified_file_list(self) -> list[File]:
        return [
            File(
                last_modify_time=os.path.getmtime(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                size=os.path.getsize(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                name=file_name,
            )
            for file_name in self.TEST_SORT_LAST_MODIFIED_FILE_NAME_LIST
        ]

    def test_sort_file_list__last_modified__ascending(self):
        # arrange
        file_list = self._prepare_sort_last_modified_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.LAST_MODIFY.value, sort_dir=OrderDirection.ASCENDING.value)

        # assert
        self.assertEqual(
            [file.name for file in file_list],
            ['test_last_modified_first_mod', 'test_last_modified_second_mod', 'test_last_modified_third_mod'],
        )

    def test_sort_file_list__last_modified__descending(self):
        # arrange
        file_list = self._prepare_sort_last_modified_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.LAST_MODIFY.value, sort_dir=OrderDirection.DESCENDING.value)

        # assert
        self.assertEqual(
            [file.name for file in file_list],
            ['test_last_modified_third_mod', 'test_last_modified_second_mod', 'test_last_modified_first_mod'],
        )

    def _prepare_sort_size_file_list(self) -> list[File]:
        return [
            File(
                last_modify_time=os.path.getmtime(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                size=os.path.getsize(self.PROJECT_ROOT_PATH / self.TEST_DIR / file_name),
                name=file_name,
            )
            for file_name in self.TEST_SORT_SIZE_FILE_NAME_CONTENT_MAP.keys()
        ]

    def test_sort_file_list__size__ascending(self):
        # arrange
        file_list = self._prepare_sort_size_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.SIZE.value, sort_dir=OrderDirection.ASCENDING.value)

        # assert
        self.assertEqual(
            [file.name for file in file_list],
            ['test_size_small', 'test_size_medium', 'test_size_large'],
        )

    def test_sort_file_list__size__descending(self):
        # arrange
        file_list = self._prepare_sort_size_file_list()

        # action
        sort_file_list(file_list, sort_by=FileAttr.LAST_MODIFY.value, sort_dir=OrderDirection.DESCENDING.value)

        # assert
        self.assertEqual(
            [file.name for file in file_list],
            ['test_size_large', 'test_size_medium', 'test_size_small'],
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.PROJECT_ROOT_PATH / cls.TEST_DIR)


