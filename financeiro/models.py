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
    
    STATUS_CHOICES = [
        ('pago', 'Pago'),
        ('pendente', 'Pendente'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    
    data_despesa = models.DateField()
    data_vencimento = models.DateField()
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


class Receita(models.Model):
    """
    Modelo para registro de receitas além das reservas (aluguel, freelas, etc).
    """
    CATEGORIA_CHOICES = [
        ('aluguel', 'Aluguel de Ponto Comercial'),
        ('freela', 'Serviços Freelancer'),
        ('eventos', 'Eventos'),
        ('produtos', 'Venda de Produtos'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('pendente', 'Pendente'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    
    data_receita = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    
    comprovante = models.FileField(upload_to='receitas/', blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    recorrente = models.BooleanField(default=False, help_text='Se é uma receita recorrente (mensal)')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        ordering = ['-data_receita']
    
    def __str__(self):
        return f'Receita: {self.descricao} - R$ {self.valor}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando uma receita é criada ou atualizada.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova receita registrada: {self.descricao} - R$ {self.valor}')
        else:
            logger.info(f'Receita atualizada: {self.id} - {self.descricao}')


class Alerta(models.Model):
    """
    Modelo para registro de alertas e notificações do sistema financeiro.
    """
    TIPO_CHOICES = [
        ('reserva_pendente', 'Reserva com Pagamento Pendente'),
        ('despesa_vencendo', 'Despesa Próxima do Vencimento'),
        ('receita_atrasada', 'Receita em Atraso'),
        ('ocupacao_baixa', 'Baixa Ocupação'),
        ('manutencao', 'Manutenção Necessária'),
        ('estoque', 'Estoque Baixo'),
        ('outros', 'Outros'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_vencimento = models.DateField(null=True, blank=True)
    
    # Relacionamentos opcionais
    reserva = models.ForeignKey('reservas.Reserva', on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    despesa = models.ForeignKey(Despesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    receita = models.ForeignKey(Receita, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    
    visualizado = models.BooleanField(default=False)
    resolvido = models.BooleanField(default=False)
    data_resolucao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-prioridade', '-data_criacao']
    
    def __str__(self):
        return f'Alerta: {self.titulo} - {self.get_prioridade_display()}'
    
    def marcar_como_resolvido(self):
        """
        Marca o alerta como resolvido e registra a data de resolução.
        """
        self.resolvido = True
        self.data_resolucao = timezone.now()
        self.save()
        logger.info(f'Alerta {self.id} - {self.titulo} marcado como resolvido')
    
    def marcar_como_visualizado(self):
        """
        Marca o alerta como visualizado.
        """
        self.visualizado = True
        self.save()
        logger.info(f'Alerta {self.id} - {self.titulo} marcado como visualizado')
