from django.db import models
from django.utils import timezone
from reservas.models import Reserva
import logging

logger = logging.getLogger(__name__)

class Pagamento(models.Model):
    """
    Modelo para registro e controle de pagamentos.
    Permite registrar pagamentos associados a reservas.
    """
    TIPO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência Bancária'),
        ('deposito', 'Depósito Bancário'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('aprovado', 'Aprovado'),
        ('pendente', 'Pendente'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado'),
    ]
    
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name='pagamentos')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    
    data_pagamento = models.DateTimeField(default=timezone.now)
    codigo_transacao = models.CharField(max_length=50, blank=True, null=True)
    comprovante = models.FileField(upload_to='comprovantes/', blank=True, null=True)
    
    observacoes = models.TextField(blank=True, null=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f'Pagamento {self.id} - R$ {self.valor} - {self.reserva.codigo}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando um pagamento é criado ou atualizado.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo pagamento registrado: R$ {self.valor} para reserva {self.reserva.codigo}')
        else:
            logger.info(f'Pagamento atualizado: {self.id} - Status: {self.status}')


class Despesa(models.Model):
    """
    Modelo para registro e controle de despesas da pousada.
    """
    CATEGORIA_CHOICES = [
        ('manutencao', 'Manutenção'),
        ('limpeza', 'Limpeza'),
        ('alimentacao', 'Alimentação'),
        ('energia', 'Energia Elétrica'),
        ('agua', 'Água'),
        ('internet', 'Internet'),
        ('funcionarios', 'Funcionários'),
        ('impostos', 'Impostos'),
        ('marketing', 'Marketing'),
        ('outros', 'Outros'),
    ]
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    
    data_despesa = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    
    comprovante = models.FileField(upload_to='despesas/', blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa']
    
    def __str__(self):
        return f'Despesa: {self.descricao} - R$ {self.valor}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando uma despesa é criada ou atualizada.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova despesa registrada: {self.descricao} - R$ {self.valor}')
        else:
            logger.info(f'Despesa atualizada: {self.id} - {self.descricao}')
