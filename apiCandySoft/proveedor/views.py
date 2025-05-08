from django.shortcuts import render
from rest_framework import  viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from .models import Proveedor
from .serializer import ProveedorSerializer

# Create your views here.

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer;
    permission_classes = [AllowAny];
    
