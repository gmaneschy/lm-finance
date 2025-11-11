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
