from django.db import models
from django.utils import timezone
# Create your models here.

# =======================
#  MODELO DE MATÉRIA-PRIMA
# =======================
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
        return f"{self.nome} {self.categoria} {self.especificacao} {self.cor} ({self.get_categoria_display()})"


# =======================
#  MODELO DE COMPRA DE MATÉRIA-PRIMA
# =======================
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
        return (f"Compra de "
                f"{self.materia_prima.nome} {self.unidade_em_quantidade} "
                f"{self.unidade_em_cm} {self.preco} {self.unidade.lower()}")
