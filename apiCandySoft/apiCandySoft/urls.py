"""
URL configuration for apiCandySoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    
    #rutas de api para admin 
    path('admin/', admin.site.urls),
    
    #rutas de api para swagger y redoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    #rutas de api para los diferentes modulos
    path('api/rol/',include("rol.urls")),
    path('api/servicio/',include("servicio.urls")),
    path('api/usuario/',include('usuario.urls')),
    path('api/cita-venta/',include('cita.urls')),
    path('api/auth/',include('authrecuperacion.urls')),
    path('api/manicurista/',include('manicurista.urls')),
    path('api/proveedor/',include('proveedor.urls')),
    path('api/insumo/',include('insumo.urls')),
    path('api/compras/',include('compra.urls')),
    path('api/abastecimiento/',include('abastecimiento.urls')),
]