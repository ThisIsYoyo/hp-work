import os
import re
from pathlib import Path

from django.db import transaction
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .define import FileAttr, OrderDirection, check_parameter_follow_defined


@api_view(['GET'])
# @renderer_classes
def index(request):
    return Response('Hello, World. This is simple Response for index!', status=status.HTTP_200_OK)


class File:
    def __init__(self, last_modify_time: float, size: int, name: str):
        self.last_modify_time = last_modify_time
        self.size = size
        self.name = name


def filter_file_under_path(path: Path, filter_name: str = '') -> list[File]:
    return [
        File(
            last_modify_time=os.path.getmtime(path / file_name),
            size=os.path.getsize(path / file_name),
            name=file_name,
        )
        for file_name in os.listdir(path)
        if re.compile(rf'{filter_name}').search(file_name) and os.path.isfile(path / file_name)
    ]


def sort_file_list(
        file_list: list[File],
        sort_by: str = FileAttr.NAME.value,
        sort_dir: str = OrderDirection.ASCENDING.value
) -> None:
    file_list.sort(
        key=lambda file: {
            FileAttr.LAST_MODIFY.value: file.last_modify_time,
            FileAttr.SIZE.value: file.size,
            FileAttr.NAME.value: file.name,
        }[sort_by],
        reverse=(sort_dir == OrderDirection.DESCENDING.value),
    )


class FileView(APIView):
    PROJECT_ROOT_PATH = Path(__file__).parent.parent.parent

    @transaction.atomic
    def get(self, reqeust, file_path):
        full_file_path = self.PROJECT_ROOT_PATH / file_path

        if full_file_path.is_dir():
            order_by = reqeust.GET.get('orderBy') or FileAttr.NAME.value
            if not check_parameter_follow_defined(order_by, FileAttr):
                return Response(f'orderBy: {order_by} is not available', status.HTTP_400_BAD_REQUEST)

            order_by_direction = reqeust.GET.get('orderByDirection') or OrderDirection.ASCENDING.value
            if not check_parameter_follow_defined(order_by_direction, OrderDirection):
                return Response(f'orderByDirection: {order_by_direction} is not available', status.HTTP_400_BAD_REQUEST)

            filter_by_name = reqeust.GET.get('filterByName', '')

            file_list = filter_file_under_path(full_file_path, filter_by_name)
            sort_file_list(file_list, order_by, order_by_direction)

            return Response(
                {
                    'isDirectory': True,
                    'files': [file.name for file in file_list],
                },
                status=status.HTTP_200_OK
            )
        elif full_file_path.is_file():
            return FileResponse(open(full_file_path, 'rb'))

        return Response(f'/{file_path} not exist', status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def post(self, request, file_path):
        full_file_path = self.PROJECT_ROOT_PATH / file_path

        if full_file_path.is_file():
            return Response(f'/{file_path} already exist.', status=status.HTTP_400_BAD_REQUEST)

        file_content = request.POST.get('file', '')
        with open(full_file_path, 'w') as fp:
            fp.write(file_content)

        return Response(f'/{file_path} created', status=status.HTTP_201_CREATED)

    @transaction.atomic
    def patch(self, request, file_path):
        full_file_path = self.PROJECT_ROOT_PATH / file_path

        if not full_file_path.is_file():
            return Response(f'/{file_path} not exist.', status=status.HTTP_400_BAD_REQUEST)

        file_content = request.data.get('file', '')
        with open(full_file_path, 'w') as fp:
            fp.write(file_content)

        return Response(f'/{file_path} updated.', status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, file_path):
        full_file_path = self.PROJECT_ROOT_PATH / file_path

        if full_file_path.is_file():
            os.remove(full_file_path)
            return Response(f'/{file_path} removed.', status=status.HTTP_200_OK)

        elif full_file_path.is_dir():
            return Response(f'/{file_path} is a directory.', status=status.HTTP_400_BAD_REQUEST)

        return Response(f'/{file_path} not exist.', status=status.HTTP_400_BAD_REQUEST)
