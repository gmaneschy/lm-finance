from django.db import models
from django.utils import timezone
from decimal import Decimal


# Create your models here.
class MateriaPrima(models.Model):
    C_CATEGORIA = [
        ('FITA', 'Fita'),
        ('LINHA', 'Linha'),
        ('ENFEITE', 'Enfeite'),
        ('PRESILHA', 'Presilha'),
        ('ARCO', 'Arco'),
        ('OUTROS', 'Outros'),
    ]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100, choices=C_CATEGORIA)
    especificacao = models.CharField(max_length=100)
    cor = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.especificacao}) ({self.cor}) ({self.get_categoria_display()})"


class CompraMateriaPrima(models.Model):
    C_UNIDADE = [
        ('QUANTIDADE', 'Quantidade'),
        ('CM', 'Centímetro'),
    ]

    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='compras')
    unidade = models.CharField(max_length=20, choices=C_UNIDADE)
    unidade_em_quantidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unidade_em_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_por_quantidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_por_cm = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.CharField(max_length=100, blank=True, null=True, default='Genérico')
    fornecedor = models.CharField(max_length=100, blank=True, null=True)
    data_compra = models.DateField(default=timezone.now)

    def __str__(self):
        return (f"{self.materia_prima.nome} ({self.marca}) - "
                f"{self.preco} R$ - {self.get_unidade_display()}")


class Produto(models.Model):
    CATEGORIAS = [
        ('LACO', 'Laço'),
        ('TIARA', 'Tiara'),
        ('FAIXA', 'Faixa'),
    ]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    quantidade_em_estoque = models.PositiveIntegerField(default=0)
    custo_fixo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Custo fixo UNITÁRIO
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lucro_por_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_cadastro = models.DateField(default=timezone.now)

    def __str__(self):
        return self.nome

    @property
    def custo_total(self):
        total_materiais = sum([m.valor_total for m in self.materiais_usados.all()])
        return total_materiais + (self.custo_fixo_total or 0)

    @property
    def valor_total(self):
        return self.custo_total * self.quantidade_em_estoque


class MaterialUsado(models.Model):
    """
    Modelo atualizado com tipo de unidade próprio
    """
    C_UNIDADE = [
        ('QUANTIDADE', 'Quantidade'),
        ('CM', 'Centímetro'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="materiais_usados")
    compra_materia_prima = models.ForeignKey('CompraMateriaPrima', on_delete=models.CASCADE, null=True, blank=True)
    tipo_unidade = models.CharField(max_length=20, choices=C_UNIDADE, default='CM')
    qtd_material_usado = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def valor_unitario(self):
        """
        Retorna o valor unitário baseado no tipo de unidade selecionado
        """
        compra = self.compra_materia_prima
        if not compra:
            return Decimal(0)

        # Usa o tipo_unidade do MaterialUsado, não da CompraMateriaPrima
        if self.tipo_unidade == 'CM':
            return compra.valor_por_cm or Decimal(0)
        return compra.valor_por_quantidade or Decimal(0)

    @property
    def valor_total(self):
        return self.valor_unitario * self.qtd_material_usado

    def __str__(self):
        if self.compra_materia_prima:
            return f"{self.compra_materia_prima.materia_prima.nome} ({self.qtd_material_usado} {self.get_tipo_unidade_display()})"
        return f"Material ({self.qtd_material_usado})"


class CustoFixo(models.Model):
    energia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cola = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    isqueiro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    das_mei = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxas_bancarias = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # NOVOS CAMPOS
    papeleta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    embalagem = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    etiqueta = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def custo_fixo_total(self):
        return sum([
            self.energia, self.cola, self.isqueiro,
            self.das_mei, self.taxas_bancarias,
            self.papeleta, self.embalagem, self.etiqueta
        ])

    def __str__(self):
        return f"Custo Fixo Total Unitário: R$ {self.custo_fixo_total:.2f}"


# NOVO MODELO: CUSTO FIXO MENSAL para registro de despesas reais (Conforme planilha)
class CustoFixoMensal(models.Model):
    """
    Registra a despesa REAL de custos fixos no mês de referência.
    Usado para calcular o Lucro Líquido mensal.
    """
    data_referencia = models.DateField(
        unique=True,
        help_text="Primeiro dia do mês ao qual este custo fixo se refere (Ex: 2025-01-01)"
    )
    energia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cola = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    isqueiro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    das_mei = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxas_bancarias = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Taxas da maquininha
    papeleta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    embalagem = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    etiqueta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Novo campo para custos variáveis que não são matéria-prima (Frete, Marketing)
    outros_variaveis = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def custo_variavel_total(self):
        """Calcula a soma de todos os custos variáveis listados na planilha (energia, papelaria, etc.)"""
        return sum([
            self.energia, self.cola, self.isqueiro,
            self.papeleta, self.embalagem, self.etiqueta,
            self.outros_variaveis
        ])

    @property
    def custo_fixo_total(self):
        """Calcula a soma de custos fixos MEI (DAS MEI e Taxas)"""
        return self.das_mei + self.taxas_bancarias

    def __str__(self):
        return f"Custos de {self.data_referencia.strftime('%B/%Y')} - Variável: R$ {self.custo_variavel_total:.2f}"

    class Meta:
        verbose_name = "Custo Mensal (Variável e Fixo)"
        verbose_name_plural = "Custos Mensais (Variáveis e Fixos)"


class Estoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE)
    quantidade_produto = models.PositiveIntegerField(default=0)
    valor_produto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    materia_prima_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    produto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def atualizar_valores(self):
        self.valor_produto = self.produto.custo_total
        self.produto_total = self.valor_produto * self.quantidade_produto
        self.materia_prima_total = sum([m.valor_total for m in self.produto.materiais_usados.all()])
        self.save()

    def __str__(self):
        return f"Estoque de {self.produto.nome}"


class Venda(models.Model):
    METODOS_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
    ]

    data_venda = models.DateTimeField(default=timezone.now)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pagamento = models.CharField(max_length=20, choices=METODOS_PAGAMENTO, default='PIX')
    observacao = models.TextField(blank=True, null=True)
    cliente_nome = models.CharField(max_length=100, blank=True, null=True, default="Cliente Balcão")

    def __str__(self):
        return f"Venda #{self.id} - {self.data_venda.strftime('%d/%m/%Y')} - R$ {self.valor_total}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)

    # === CORREÇÃO CRÍTICA AQUI: SET_NULL + null=True ===
    # Ao deletar o Produto, a FK é definida como NULL, preservando o histórico de vendas.
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,  # Permite que o campo seja NULL no banco de dados.
        related_name='itens_vendidos'
    )
    # ===================================================

    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Novo campo para armazenar o custo do produto no momento da venda (snapshot)
    custo_unitario_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Custo do produto no momento da venda (para relatórios)"
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.valor_unitario
        # Se for um item novo, registra o custo do produto no momento (snapshot)
        if not self.pk and self.produto:
            # Usando o custo total do produto no momento da venda
            self.custo_unitario_snapshot = self.produto.custo_total
        super().save(*args, **kwargs)

    def __str__(self):
        # Adiciona um tratamento para produtos que foram deletados (quando o produto for None)
        nome_produto = self.produto.nome if self.produto else "Produto Deletado (ID Histórico)"
        return f"{self.quantidade}x {nome_produto} (Venda #{self.venda.id})"


class LancamentoFinanceiro(models.Model):
    TIPO_LANCAMENTO = [
        ('ENTRADA', 'Entrada (Receita)'),
        ('SAIDA', 'Saída (Despesa)'),
    ]
    CATEGORIAS = [
        ('VENDA', 'Venda de Produtos'),
        ('COMPRA_MATERIAL', 'Compra de Matéria Prima'),
        ('CUSTO_FIXO', 'Custos Fixos (Luz, MEI, etc)'),
        ('OUTROS', 'Outros'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_LANCAMENTO)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(default=timezone.now)

    # Campo opcional para ligar uma venda a esse lançamento financeiro
    venda_origem = models.OneToOneField('Venda', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='lancamento_financeiro')

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - R$ {self.valor}"


# NOVO MODELO: Metas Financeiras (Recomendação MEI)
class MetasFinanceiras(models.Model):
    """
    Armazena as metas mensais para acompanhamento de desempenho.
    """
    data_referencia = models.DateField(
        unique=True,
        help_text="Primeiro dia do mês ao qual a meta se refere (Ex: 2025-01-01)"
    )
    # Limite MEI (anual R$ 81.000,00 - mensal R$ 6.750,00)
    meta_faturamento_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('6750.00'),
        help_text="Meta mensal de faturamento (Limite MEI é R$ 6.750,00)"
    )
    meta_lucro_liquido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meta_quantidade_vendas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Metas para {self.data_referencia.strftime('%B/%Y')}"