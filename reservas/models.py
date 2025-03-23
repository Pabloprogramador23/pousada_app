from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from quartos.models import Quarto
from hospedes.models import Hospede
import logging
import uuid

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
    
    def clean(self):
        """
        Valida que a data de check-in é anterior à data de check-out.
        """
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError('A data de check-in deve ser anterior à data de check-out.')
            
            # Verifica sobreposição de reservas para o mesmo quarto
            reservas_sobrepostas = Reserva.objects.filter(
                quarto=self.quarto,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in
            ).exclude(pk=self.pk)
            
            if reservas_sobrepostas.exists():
                raise ValidationError('Já existe uma reserva para este quarto no período selecionado.')
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para gerar o código da reserva, calcular o valor total
        e registrar no log quando uma reserva é criada ou atualizada.
        """
        # Gera código da reserva se não existir
        if not self.codigo:
            # Usa UUID para gerar um código único
            uid = str(uuid.uuid4()).replace('-', '')[:8].upper()
            self.codigo = f'RES{timezone.now().strftime("%y%m%d")}{uid}'
        
        # Calcula o valor da diária e o valor total
        if not self.valor_diaria and self.quarto:
            self.valor_diaria = self.quarto.preco_diaria
            
        if self.check_in and self.check_out and self.valor_diaria:
            dias = (self.check_out - self.check_in).days
            self.valor_total = self.valor_diaria * dias
        
        # Atualiza flags de acordo com o status
        if self.status == 'confirmada':
            self.confirmada = True
            self.cancelada = False
        elif self.status == 'cancelada':
            self.cancelada = True
            self.confirmada = False
        
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
