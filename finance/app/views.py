from django.shortcuts import render, redirect
from .forms import MateriaPrimaForm, CompraMateriaPrimaForm

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


def estoque(request):
    return render(request, 'estoque.html')