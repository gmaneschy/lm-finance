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

    # Páginas principais
    path('', views.estoque, name='estoque'),
    path('templates/registradora/', views.registradora, name='registradora'),
    path('autocomplete/marcas/', views.autocomplete_marcas, name='autocomplete_marcas'),
    path('autocomplete/fornecedores/', views.autocomplete_fornecedores, name='autocomplete_fornecedores'),
    path('templates/cadastrar_produto/', views.cadastrar_produto, name='cadastrar_produto'),

    # Página de Estoque
    path('templates/estoque/', views.estoque, name='estoque'),

    # API Produtos
    path('api/produtos/<int:id>/', views.api_produto_detalhe, name='api_produto_detalhe'),
    path('api/produtos/<int:id>/editar/', views.api_produto_editar, name='api_produto_editar'),
    path('api/produtos/<int:id>/excluir/', views.api_produto_excluir, name='api_produto_excluir'),

    # API Matérias-Primas
    path('api/materias/<int:id>/', views.api_materia_detalhe, name='api_materia_detalhe'),
    path('api/materias/<int:id>/editar/', views.api_materia_editar, name='api_materia_editar'),
    path('api/materias/<int:id>/excluir/', views.api_materia_excluir, name='api_materia_excluir'),

    path('templates/vendas/', views.vendas, name='vendas'),
    path('api/salvar_venda/', views.api_salvar_venda, name='api_salvar_venda'),  # Nova rota
    path('templates/financeiro/', views.financeiro, name='financeiro'),
    path('api/custo-produto/', views.get_custo_produto_json, name='api_custo_produto'),
]
