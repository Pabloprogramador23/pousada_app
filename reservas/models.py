from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from quartos.models import Quarto
from hospedes.models import Hospede
import logging
import uuid
from datetime import datetime, time
import math
import random
import string

logger = logging.getLogger(__name__)

class Reserva(models.Model):
    """
    Modelo para gerenciamento de reservas de quartos.
    Associa hóspedes a quartos em períodos específicos.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
        ('no_show', 'No-show'),
    ]
    
    ORIGEM_CHOICES = [
        ('site', 'Site Próprio'),
        ('telefone', 'Telefone'),
        ('presencial', 'Presencial'),
        ('booking', 'Booking'),
        ('airbnb', 'Airbnb'),
        ('outros', 'Outros'),
    ]
    
    # Informações básicas
    codigo = models.CharField('Código', max_length=20, unique=True)
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT, related_name='reservas', verbose_name='Quarto')
    hospede = models.ForeignKey(Hospede, on_delete=models.PROTECT, related_name='reservas', verbose_name='Hóspede')
    
    # Período da reserva
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    quantidade_hospedes = models.PositiveSmallIntegerField(default=1)
    quantidade_adultos = models.PositiveSmallIntegerField(default=1)
    quantidade_criancas = models.PositiveSmallIntegerField(default=0)
    
    # Status e origem
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    status_anterior = models.CharField(max_length=20, editable=False, null=True, blank=True)
    origem = models.CharField(max_length=50, default='site')
    confirmada = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    concluida = models.BooleanField(default=False)
    no_show = models.BooleanField(default=False)
    
    # Valores
    valor_diaria = models.DecimalField('Valor da Diária', max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, null=True, blank=True)
    valor_sinal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto_diaria = models.DecimalField('Desconto na Diária', max_digits=10, decimal_places=2, default=0)
    
    # Comentários e solicitações
    observacoes = models.TextField('Observações', blank=True, null=True)
    observacoes_admin = models.TextField(blank=True, null=True, verbose_name="Observações Administrativas")
    solicitacoes_especiais = models.TextField(blank=True, null=True)
    
    # Controle
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_cancelamento = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Reserva {self.codigo} - {self.hospede.nome}"
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-check_in']
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_depois_do_check_in'
            )
        ]
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar valores e status antes de salvar.
        """
        # Calcula o valor total da reserva
        if not self.valor_total or self.valor_total == 0:
            self.valor_total = self.calcular_total()
        
        # Atualiza os flags baseado no status
        if self.status == 'confirmada':
            self.confirmada = True
            self.cancelada = False
            self.concluida = False
            self.no_show = False
        elif self.status == 'cancelada':
            self.confirmada = False
            self.cancelada = True
            self.concluida = False
            self.no_show = False
        elif self.status == 'concluida':
            self.confirmada = False
            self.cancelada = False
            self.concluida = True
            self.no_show = False
        elif self.status == 'no_show':
            self.confirmada = False
            self.cancelada = False
            self.concluida = False
            self.no_show = True
        else:  # pendente
            self.confirmada = False
            self.cancelada = False
            self.concluida = False
            self.no_show = False
            
        # Gera código da reserva se não existir
        if not self.codigo:
            # Usa UUID para gerar um código único
            uid = str(uuid.uuid4()).replace('-', '')[:8].upper()
            self.codigo = f'RES{timezone.now().strftime("%y%m%d")}{uid}'
            
        # Registra o status anterior para rastreamento de mudanças
        if self.pk:
            try:
                old_instance = Reserva.objects.get(pk=self.pk)
                self.status_anterior = old_instance.status
            except Reserva.DoesNotExist:
                pass
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova reserva criada: {self.codigo} para {self.hospede.nome}')
        else:
            if self.status == 'confirmada' and not self.data_confirmacao:
                self.data_confirmacao = timezone.now()
                super().save(update_fields=['data_confirmacao'])
            elif self.status == 'cancelada' and not self.data_cancelamento:
                self.data_cancelamento = timezone.now()
                super().save(update_fields=['data_cancelamento'])

    def calcular_total(self):
        """
        Calcula o valor total da reserva com base na diária, número de pessoas e período.
        """
        # Primeiro calcula o número de dias
        delta = (self.check_out - self.check_in).days
        
        # Se não há dias válidos, retorna zero
        if delta <= 0:
            return 0
        
        # Calcula o valor da diária com base no número de pessoas
        valor_base = 140.00  # Valor base para 1-2 pessoas
        
        # Número total de pessoas
        total_pessoas = self.quantidade_adultos + self.quantidade_criancas
        
        # Adiciona R$70 por pessoa adicional além de 2
        pessoas_extras = max(0, total_pessoas - 2)
        valor_diaria_calculado = valor_base + (pessoas_extras * 70.00)
        
        # Aplica desconto se houver
        if hasattr(self, 'desconto_diaria') and self.desconto_diaria:
            valor_diaria_calculado -= self.desconto_diaria
        
        # Garante que a diária não seja menor que o mínimo
        valor_diaria_calculado = max(valor_diaria_calculado, 100.00)
        
        # Atualiza o valor da diária
        self.valor_diaria = valor_diaria_calculado
        
        # Calcula o total
        return valor_diaria_calculado * delta
    
    def get_status_color(self):
        """Retorna a cor associada ao status atual da reserva."""
        colors = {
            'pendente': 'warning',
            'confirmada': 'primary',
            'em_andamento': 'success',
            'concluida': 'info',
            'cancelada': 'danger',
            'no_show': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
    def get_pagamentos_totais(self):
        """Retorna o total de pagamentos feitos para esta reserva."""
        try:
            from financeiro.models import Pagamento
            pagamentos = Pagamento.objects.filter(reserva=self).aggregate(
                total=models.Sum('valor')
            )['total'] or 0
            return float(pagamentos)
        except (ImportError, Exception) as e:
            logger.warning(f"Erro ao calcular pagamentos para reserva {self.codigo}: {e}")
            return 0
    
    def get_saldo_pendente(self):
        """Retorna o saldo pendente de pagamento."""
        return float(self.valor_total) - self.get_pagamentos_totais()
    
    def permite_pagamento(self):
        """Verifica se a reserva permite registrar novos pagamentos."""
        return self.status in ['pendente', 'confirmada', 'em_andamento']


class Historico(models.Model):
    """
    Modelo para registrar o histórico de alterações em uma reserva.
    Permite rastrear todas as mudanças realizadas.
    """
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='historicos')
    data_hora = models.DateTimeField(auto_now_add=True)
    status_anterior = models.CharField(max_length=15, choices=Reserva.STATUS_CHOICES, null=True, blank=True)
    status_novo = models.CharField(max_length=15, choices=Reserva.STATUS_CHOICES)
    descricao = models.TextField()
    
    class Meta:
        verbose_name = 'Histórico de Reserva'
        verbose_name_plural = 'Históricos de Reservas'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f'Alteração em {self.reserva.codigo} - {self.data_hora.strftime("%d/%m/%Y %H:%M")}'
