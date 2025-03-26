from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from quartos.models import Quarto
from hospedes.models import Hospede
import logging
import uuid
from datetime import datetime, time
import math

logger = logging.getLogger(__name__)

class Reserva(models.Model):
    """
    Modelo para gerenciamento de reservas de quartos.
    Associa hóspedes a quartos em períodos específicos.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('em_andamento', 'Em Andamento'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
        ('no_show', 'No-Show'),
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
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT, related_name='reservas')
    hospede = models.ForeignKey(Hospede, on_delete=models.PROTECT, related_name='reservas')
    
    # Período da reserva
    check_in = models.DateField(verbose_name="Data de Check-in")
    check_out = models.DateField(verbose_name="Data de Check-out")
    hora_checkin = models.TimeField(null=True, blank=True)
    hora_checkout = models.TimeField(null=True, blank=True)
    
    # Ocupação
    adultos = models.PositiveSmallIntegerField(default=2)
    criancas = models.PositiveSmallIntegerField(default=0)
    
    # Status e origem
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    origem = models.CharField(max_length=50, default='site')
    confirmada = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    motivo_cancelamento = models.TextField(blank=True, null=True)
    
    # Valores
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_sinal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto_diaria = models.DecimalField("Desconto por diária", max_digits=10, decimal_places=2, default=0)
    
    # Comentários e solicitações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    observacoes_admin = models.TextField(blank=True, null=True, verbose_name="Observações Administrativas")
    solicitacoes_especiais = models.TextField(blank=True, null=True)
    
    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_cancelamento = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-check_in']
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_in__lt=models.F('check_out')),
                name='check_in_anterior_check_out'
            )
        ]
    
    def __str__(self):
        return f'Reserva {self.codigo} - {self.hospede.nome}'
    
    @property
    def status_badge(self):
        """
        Retorna a classe de cor do Bootstrap para o status atual.
        """
        status_colors = {
            'pendente': 'secondary',
            'confirmada': 'primary',
            'em_andamento': 'info',
            'concluida': 'success',
            'cancelada': 'danger',
            'no_show': 'warning'
        }
        return status_colors.get(self.status, 'secondary')
    
    def clean(self):
        """
        Valida que a data de check-in é anterior à data de check-out
        e que não há sobreposição de reservas para o mesmo quarto.
        """
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError('A data de check-in deve ser anterior à data de check-out.')
            
            # Verifica sobreposição de reservas para o mesmo quarto
            # Uma reserva se sobrepõe se:
            # 1. Começa antes do check-out desta reserva E
            # 2. Termina depois do check-in desta reserva E
            # 3. Não é esta mesma reserva (em caso de atualização) E
            # 4. Não está cancelada
            reservas_sobrepostas = Reserva.objects.filter(
                quarto=self.quarto,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
                status__in=['pendente', 'confirmada', 'em_andamento']
            ).exclude(pk=self.pk)
            
            if reservas_sobrepostas.exists():
                reserva_conflitante = reservas_sobrepostas.first()
                raise ValidationError(
                    f'Já existe uma reserva para este quarto no período selecionado. '
                    f'Reserva conflitante: {reserva_conflitante.codigo} '
                    f'({reserva_conflitante.hospede.nome}) - '
                    f'Check-in: {reserva_conflitante.check_in.strftime("%d/%m/%Y")}, '
                    f'Check-out: {reserva_conflitante.check_out.strftime("%d/%m/%Y")}'
                )
    
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
        total_pessoas = self.adultos + self.criancas
        
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
        elif self.status == 'em_andamento':
            self.confirmada = True
            self.cancelada = False
        elif self.status == 'cancelada':
            self.cancelada = True
            self.confirmada = False
        elif self.status == 'pendente':
            self.confirmada = False
            self.cancelada = False
            
        # Gera código da reserva se não existir
        if not self.codigo:
            # Usa UUID para gerar um código único
            uid = str(uuid.uuid4()).replace('-', '')[:8].upper()
            self.codigo = f'RES{timezone.now().strftime("%y%m%d")}{uid}'
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova reserva criada: {self.codigo} para {self.hospede.nome}')
        else:
            if self.status == 'confirmada' and not self.data_confirmacao:
                self.data_confirmacao = timezone.now()
                logger.info(f'Reserva confirmada: {self.codigo}')
                
            if self.status == 'cancelada' and not self.data_cancelamento:
                self.data_cancelamento = timezone.now()
                logger.info(f'Reserva cancelada: {self.codigo}')
                
            logger.info(f'Reserva atualizada: {self.codigo}')

    def get_status_color(self):
        """
        Retorna a cor correspondente ao status da reserva.
        """
        cores = {
            'pendente': '#f9c851',  # Amarelo
            'confirmada': '#34c38f', # Verde
            'em_andamento': '#556ee6', # Azul
            'concluida': '#50a5f1',  # Azul claro
            'cancelada': '#f46a6a',  # Vermelho
            'no_show': '#74788d'     # Cinza
        }
        return cores.get(self.status, '#74788d')


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
