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


class ProdutoForm(forms.ModelForm):
    # Campo extra para exibir custo total estimado
    custo_total_estimado = forms.DecimalField(
        label='Custo Total Estimado (R$)',
        required=False,
        disabled=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control campo-automatico',
            'readonly': 'readonly',
            'id': 'id_custo_total_estimado'
        })
    )

    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'quantidade_em_estoque', 'valor_venda', 'lucro_por_venda']
        labels = {
            'nome': 'Nome do Produto',
            'categoria': 'Categoria',
            'quantidade_em_estoque': 'Quantidade em Estoque',
            'valor_venda': 'Valor de Venda (R$)',
            'lucro_por_venda': 'Lucro por Venda (R$)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_em_estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valor_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lucro_por_venda': forms.NumberInput(attrs={
                'class': 'form-control campo-automatico',
                'step': '0.01',
                'readonly': 'readonly',
                'id': 'id_lucro_por_venda'
            }),
        }


class MaterialUsadoForm(forms.ModelForm):
    class Meta:
        model = MaterialUsado
        fields = ['compra_materia_prima', 'tipo_unidade', 'qtd_material_usado']
        labels = {
            'compra_materia_prima': 'Material',
            'tipo_unidade': 'Tipo de Unidade',
            'qtd_material_usado': 'Quantidade',
        }
        widgets = {
            'compra_materia_prima': forms.Select(attrs={'class': 'form-control material-select'}),
            'tipo_unidade': forms.Select(attrs={'class': 'form-control tipo-unidade-select'}),
            'qtd_material_usado': forms.NumberInput(attrs={
                'class': 'form-control qtd-material-input',
                'step': '0.01',
                'placeholder': 'Quantidade'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Melhora a exibição dos materiais no select
        self.fields['compra_materia_prima'].queryset = CompraMateriaPrima.objects.select_related('materia_prima').all()
        self.fields['compra_materia_prima'].label_from_instance = lambda obj: (
            f"{obj.materia_prima.nome} - {obj.marca}"
        )


class CustoFixoForm(forms.ModelForm):
    # Campo para bloquear/desbloquear edição
    bloqueado = forms.BooleanField(
        required=False,
        initial=True,
        label='Bloquear edição',
        widget=forms.CheckboxInput(attrs={
            'id': 'id_custos_bloqueados',
            'class': 'checkbox-bloqueio'
        })
    )

    class Meta:
        model = CustoFixo
        fields = ['energia', 'cola', 'isqueiro', 'das_mei', 'taxas_bancarias']
        labels = {
            'energia': 'Energia (R$)',
            'cola': 'Cola (R$)',
            'isqueiro': 'Isqueiro (R$)',
            'das_mei': 'DAS MEI (R$)',
            'taxas_bancarias': 'Taxas Bancárias (R$)',
        }
        widgets = {
            'energia': forms.NumberInput(attrs={
                'class': 'form-control custo-fixo-input',
                'step': '0.01',
                'value': '0',
                'readonly': 'readonly'
            }),
            'cola': forms.NumberInput(attrs={
                'class': 'form-control custo-fixo-input',
                'step': '0.01',
                'value': '0',
                'readonly': 'readonly'
            }),
            'isqueiro': forms.NumberInput(attrs={
                'class': 'form-control custo-fixo-input',
                'step': '0.01',
                'value': '0',
                'readonly': 'readonly'
            }),
            'das_mei': forms.NumberInput(attrs={
                'class': 'form-control custo-fixo-input',
                'step': '0.01',
                'value': '0',
                'readonly': 'readonly'
            }),
            'taxas_bancarias': forms.NumberInput(attrs={
                'class': 'form-control custo-fixo-input',
                'step': '0.01',
                'value': '0',
                'readonly': 'readonly'
            }),
        }