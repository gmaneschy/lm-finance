from django import forms
from .models import MateriaPrima, CompraMateriaPrima
from .models import Produto, MaterialUsado, CustoFixo

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nome', 'categoria', 'especificacao', 'cor']
        labels = {
            'nome': 'Nome da Matéria-Prima',
            'categoria': 'Categoria',
            'especificacao': 'Especificação',
            'cor': 'Cor (opcional)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'especificacao': forms.TextInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CompraMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = CompraMateriaPrima
        fields = [
            'materia_prima', 'unidade',
            'unidade_em_quantidade', 'unidade_em_cm',
            'valor_por_quantidade', 'valor_por_cm',
            'preco', 'marca', 'fornecedor', 'data_compra'
        ]
        labels = {
            'materia_prima': 'Matéria-Prima',
            'unidade': 'Tipo de Unidade',
            'unidade_em_quantidade': 'Quantidade (un)',
            'unidade_em_cm': 'Tamanho (cm)',
            'valor_por_quantidade': 'Valor por Unidade (R$)',
            'valor_por_cm': 'Valor por Centímetro (R$)',
            'preco': 'Preço Total (R$)',
            'marca': 'Marca',
            'fornecedor': 'Fornecedor',
            'data_compra': 'Data da Compra',
        }
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-control'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'unidade_em_quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidade_em_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_por_quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_por_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'data_compra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


