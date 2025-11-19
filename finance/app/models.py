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
        return (f"Compra de {self.materia_prima.nome} ({self.marca}) - "
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
    custo_fixo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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

    @property
    def custo_fixo_total(self):
        return sum([
            self.energia, self.cola, self.isqueiro,
            self.das_mei, self.taxas_bancarias
        ])

    def __str__(self):
        return f"Custo Fixo Total: R$ {self.custo_fixo_total:.2f}"


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
    produto = models.ForeignKey('Produto', on_delete=models.PROTECT, related_name='vendas')
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    data_venda = models.DateField(default=timezone.now)
    observacao = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.valor_total = (self.valor_unitario or 0) * (self.quantidade or 0)
        super().save(*args, **kwargs)
        # atualiza estoque associado se existir
        try:
            estoque = self.produto.estoque
            estoque.quantidade_produto = max(0, estoque.quantidade_produto - self.quantidade)
            estoque.atualizar_valores()
        except Exception:
            pass

    def __str__(self):
        return f"Venda: {self.produto.nome} - {self.quantidade}x ({self.data_venda})"


class Despesa(models.Model):
    CATEGORIA = [
        ('CUSTO_FIXO', 'Custo Fixo'),
        ('CUSTO_VARIAVEL', 'Custo Variável'),
        ('OUTROS', 'Outros'),
    ]
    descricao = models.CharField(max_length=150)
    categoria = models.CharField(max_length=30, choices=CATEGORIA, default='OUTROS')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(default=timezone.now)
    recorrente = models.BooleanField(default=False)  # por ex. mensal

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.data})"