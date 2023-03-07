from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response


@api_view(['GET'])
# @renderer_classes
def index(request):
    return Response('Hello, World. This is simple Response for index!', status=status.HTTP_200_OK)
