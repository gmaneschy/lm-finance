"""
URL configuration for finance project.

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
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('templates/index/', views.index, name='index'),
    path('templates/registradora/', views.registradora, name='registradora'),
    path('autocomplete/marcas/', views.autocomplete_marcas, name='autocomplete_marcas'),
    path('autocomplete/fornecedores/', views.autocomplete_fornecedores, name='autocomplete_fornecedores'),

    path('templates/cadastrar_produto/', views.cadastrar_produto, name='cadastrar_produto'),
    path('templates/financeiro/', views.financeiro, name='financeiro'),
    path('templates/estoque/', views.estoque, name='estoque'),

    # endpoints AJAX / API simples
    path('api/estoque/update/', views.api_update_estoque, name='api_update_estoque'),
    path('api/venda/create/', views.api_create_venda, name='api_create_venda'),
    path('api/despesa/create/', views.api_create_despesa, name='api_create_despesa'),

    path('api/financeiro/resumo/', views.api_financeiro_resumo, name='api_financeiro_resumo'),
    path('api/financeiro/venda/', views.api_registrar_venda, name='api_registrar_venda'),
    path('api/financeiro/despesa/', views.api_registrar_despesa, name='api_registrar_despesa'),
]