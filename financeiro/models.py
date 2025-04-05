from django.db import models
from django.core.validators import MinValueValidator


class Despesa(models.Model):
    TIPO_CHOICES = [
        ('agua', 'Água'),
        ('luz', 'Luz'),
        ('telefone', 'Telefone'),
        ('pessoal', 'Despesas Pessoais'),
        ('outros', 'Outros'),
    ]

    valor = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} em {self.data}"


class EntradaExtra(models.Model):
    ORIGEM_CHOICES = [
        ('aluguel', 'Aluguel'),
        ('outros', 'Outros'),
    ]

    valor = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    data = models.DateField()
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_origem_display()} - R$ {self.valor} em {self.data}"
