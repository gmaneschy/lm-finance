from django import forms
from .models import MateriaPrima, CompraMateriaPrima
from .models import Produto, MaterialUsado, CustoFixo, CustoFixoMensal


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
    # Campos que são propriedades (readonly/calculated)
    # Estes campos são definidos como atributos de classe e são incluídos
    # automaticamente em self.fields após super().__init__().
    custo_total_estimado = forms.DecimalField(
        label='Custo Total (Estimado)',
        required=False,
        disabled=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    lucro_por_venda = forms.DecimalField(
        label='Lucro por Venda (R$)',
        required=False,
        disabled=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'quantidade_em_estoque', 'valor_venda']
        labels = {
            'nome': 'Nome do Produto',
            'categoria': 'Categoria',
            'quantidade_em_estoque': 'Quantidade em Estoque',
            'valor_venda': 'Valor de Venda (R$)',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_em_estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'valor_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    # ❌ O méto do __init__ anterior foi removido pois estava causando o AttributeError
    # ao tentar reatribuir campos já definidos como atributos de classe.
    # O formulário funciona corretamente sem este méto do ou com ele apenas chamando super().__init__().


class MaterialUsadoForm(forms.ModelForm):
    class Meta:
        model = MaterialUsado
        fields = ['compra_materia_prima', 'tipo_unidade', 'qtd_material_usado']
        labels = {
            'compra_materia_prima': 'Material',
            'tipo_unidade': 'Unidade Utilizada',
            'qtd_material_usado': 'Qtd. Utilizada',
        }
        widgets = {
            # Classes para o JS
            'compra_materia_prima': forms.Select(attrs={'class': 'form-control material-select'}),
            'tipo_unidade': forms.Select(attrs={'class': 'form-control tipo-unidade-select'}),
            'qtd_material_usado': forms.NumberInput(
                attrs={'class': 'form-control qtd-material-input', 'step': '0.01', 'min': '0'}),
        }


class CustoFixoForm(forms.ModelForm):
    class Meta:
        model = CustoFixo
        fields = '__all__'
        labels = {
            'energia': 'Energia (R$)',
            'cola': 'Cola (R$)',
            'isqueiro': 'Isqueiro/Fósforo (R$)',
            'das_mei': 'DAS MEI (R$)',
            'taxas_bancarias': 'Taxas Bancárias (R$)',
            # NOVOS LABELS
            'papeleta': 'Papeleta (R$)',
            'embalagem': 'Embalagem (R$)',
            'etiqueta': 'Etiqueta (R$)',
        }
        widgets = {
            # Classes para o JS
            'energia': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'cola': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'isqueiro': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'das_mei': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'taxas_bancarias': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            # NOVOS WIDGETS
            'papeleta': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'embalagem': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
            'etiqueta': forms.NumberInput(attrs={'class': 'form-control custo-fixo-input', 'step': '0.01'}),
        }


class CustoMensalForm(forms.ModelForm):
    class Meta:
        model = CustoFixoMensal
        fields = [
            'energia', 'cola', 'isqueiro',
            'papeleta', 'embalagem', 'etiqueta',
            'taxas_bancarias', 'das_mei', 'outros_variaveis'
        ]
        labels = {
            'energia': 'Energia Elétrica (R$)',
            'cola': 'Gasto com Cola/Adesivos (R$)',
            'isqueiro': 'Gasto com Isqueiro/Gás (R$)',
            'papeleta': 'Papeletas/Tags (R$)',
            'embalagem': 'Embalagens/Sacolas (R$)',
            'etiqueta': 'Etiquetas (R$)',
            'taxas_bancarias': 'Taxas da Maquininha/Banco (R$)',
            'das_mei': 'DAS MEI (R$)',
            'outros_variaveis': 'Outros (Frete, Marketing, etc)',
        }
        widgets = {
            field: forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
            for field in fields
        }