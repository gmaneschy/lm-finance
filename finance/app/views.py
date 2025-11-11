from django.shortcuts import render, redirect
from .forms import MateriaPrimaForm, CompraMateriaPrimaForm
from django.http import JsonResponse
from .models import CompraMateriaPrima
from .models import Produto, MaterialUsado, Estoque
from .forms import ProdutoForm, MaterialUsadoForm, CustoFixoForm
from django.forms import modelformset_factory
from django.contrib import messages
from decimal import Decimal

from django.forms import inlineformset_factory
import json


# Create your views here.
def index(request):
    return render(request, 'index.html')

def registradora(request):
    form_mp = MateriaPrimaForm(request.POST or None)
    form_compra = CompraMateriaPrimaForm(request.POST or None)

    if request.method == 'POST':
        if 'salvar_materia' in request.POST and form_mp.is_valid():
            form_mp.save()
            return redirect('registradora')

        elif 'salvar_compra' in request.POST and form_compra.is_valid():
            form_compra.save()
            return redirect('registradora')

    return render(request, 'registradora.html', {
        'form_mp': form_mp,
        'form_compra': form_compra
    })


def cadastrar_produto(request):


    return render(request, 'cadastrar_produto.html')


def estoque(request):
    estoques = Estoque.objects.all()
    for e in estoques:
        e.atualizar_valores()
    return render(request, 'estoque.html', {'estoques': estoques})




def autocomplete_marcas(request):
    """Retorna lista de marcas únicas já registradas"""
    query = request.GET.get('q', '').lower()
    marcas = CompraMateriaPrima.objects.values_list('marca', flat=True).distinct()
    marcas_filtradas = [m for m in marcas if m and query in m.lower()]
    return JsonResponse(list(marcas_filtradas), safe=False)


def autocomplete_fornecedores(request):
    """Retorna lista de fornecedores únicos já registrados"""
    query = request.GET.get('q', '').lower()
    fornecedores = CompraMateriaPrima.objects.values_list('fornecedor', flat=True).distinct()
    fornecedores_filtrados = [f for f in fornecedores if f and query in f.lower()]
    return JsonResponse(list(fornecedores_filtrados), safe=False)