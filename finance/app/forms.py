from django import forms
from .models import MateriaPrima, CompraMateriaPrima

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nome', 'categoria', 'cor']
        labels = {
            'nome': 'Nome da Matéria-Prima',
            'categoria': 'Categoria',
            'cor': 'Cor (opcional)',
        }


class CompraMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = CompraMateriaPrima
        fields = [
            'materia_prima', 'unidade',
            'unidade_em_quantidade', 'unidade_em_cm',
            'valor_por_quantidade', 'valor_por_cm',
            'preco', 'fornecedor', 'data_compra'
        ]
        labels = {
            'materia_prima': 'Matéria-Prima',
            'unidade': 'Tipo de Unidade',
            'unidade_em_quantidade': 'Quantidade (un)',
            'unidade_em_cm': 'Tamanho (cm)',
            'valor_por_quantidade': 'Valor por Unidade (R$)',
            'valor_por_cm': 'Valor por Centímetro (R$)',
            'preco': 'Preço Total (R$)',
            'fornecedor': 'Fornecedor',
            'data_compra': 'Data da Compra',
        }