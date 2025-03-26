from django.db import models
import logging
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class CategoriaQuarto(models.Model):
    """
    Modelo para categorias de quartos da pousada.
    Permite classificar os quartos por tipo (standard, luxo, etc).
    """
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField()
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    capacidade = models.PositiveSmallIntegerField(default=2)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoria de Quarto'
        verbose_name_plural = 'Categorias de Quartos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando uma categoria é criada ou atualizada.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova categoria de quarto criada: {self.nome}')
        else:
            logger.info(f'Categoria de quarto atualizada: {self.nome}')


class Quarto(models.Model):
    """
    Modelo para quartos da pousada.
    Cada quarto pertence a uma categoria e possui um número único.
    """
    ANDAR_CHOICES = [
        ('T', 'Térreo'),
        ('1', 'Primeiro Andar'),
        ('2', 'Segundo Andar'),
        ('3', 'Terceiro Andar'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('ocupado', 'Ocupado'),
        ('manutencao', 'Em Manutenção'),
        ('limpeza', 'Em Limpeza'),
        ('reservado', 'Reservado'),
    ]
    
    numero = models.CharField(max_length=10, unique=True)
    categoria = models.ForeignKey(CategoriaQuarto, on_delete=models.PROTECT, related_name='quartos')
    andar = models.CharField(max_length=1, choices=ANDAR_CHOICES)
    area = models.DecimalField(max_digits=6, decimal_places=2, help_text='Área em metros quadrados')
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    disponivel = models.BooleanField(default=True)
    
    possui_ar_condicionado = models.BooleanField(default=True)
    possui_tv = models.BooleanField(default=True)
    possui_frigobar = models.BooleanField(default=True)
    possui_cofre = models.BooleanField(default=False)
    possui_varanda = models.BooleanField(default=False)
    
    # Campo para permitir descontos especiais
    desconto_porcentagem = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Desconto em % (0-50%) que pode ser aplicado pelo proprietário"
    )
    
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    
    ultima_limpeza = models.DateTimeField(null=True, blank=True)
    proxima_manutencao = models.DateField(null=True, blank=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quarto'
        verbose_name_plural = 'Quartos'
        ordering = ['numero']
    
    def __str__(self):
        return f'Quarto {self.numero} - {self.categoria.nome}'
    
    def preco_com_desconto(self):
        """
        Retorna o preço da diária com o desconto aplicado.
        """
        if self.preco_diaria and self.desconto_porcentagem > 0:
            desconto = (self.preco_diaria * self.desconto_porcentagem) / 100
            return self.preco_diaria - desconto
        return self.preco_diaria
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando um quarto é criado ou atualizado.
        Se o preço da diária não estiver definido, usa o preço base da categoria.
        """
        is_new = self.pk is None
        
        # Define o preço da diária caso não esteja preenchido
        if not self.preco_diaria and self.categoria:
            self.preco_diaria = self.categoria.preco_base
            
        # Atualiza o campo disponível com base no status
        self.disponivel = (self.status == 'disponivel')
        
        # Validar desconto máximo
        if self.desconto_porcentagem > 50:
            raise ValidationError("O desconto máximo permitido é de 50%")
        
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo quarto criado: {self.numero}')
        else:
            logger.info(f'Quarto atualizado: {self.numero}')
            if self.desconto_porcentagem > 0:
                logger.info(f'Desconto de {self.desconto_porcentagem}% aplicado ao quarto {self.numero}')


class FotoQuarto(models.Model):
    """
    Modelo para armazenar fotos dos quartos.
    Cada quarto pode ter múltiplas fotos.
    """
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='quartos/')
    legenda = models.CharField(max_length=100, blank=True, null=True)
    destaque = models.BooleanField(default=False)
    
    data_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Foto do Quarto'
        verbose_name_plural = 'Fotos dos Quartos'
        ordering = ['-destaque', 'quarto']
    
    def __str__(self):
        return f'Foto de {self.quarto} - {self.legenda if self.legenda else "Sem legenda"}'


class LimpezaManutencao(models.Model):
    """
    Modelo para registrar e gerenciar tarefas de limpeza e manutenção dos quartos.
    Permite acompanhar o histórico e programar futuras atividades.
    """
    TIPO_CHOICES = [
        ('limpeza', 'Limpeza'),
        ('manutencao', 'Manutenção'),
        ('vistoria', 'Vistoria'),
        ('reparo', 'Reparo'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE, related_name='tarefas')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    descricao = models.TextField()
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='agendada')
    
    data_agendamento = models.DateTimeField(default=timezone.now)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    tempo_estimado = models.PositiveIntegerField(help_text='Tempo estimado em minutos', default=30)
    
    responsavel = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True, null=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Custo em R$')
    
    checklist_completo = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tarefa de Limpeza/Manutenção'
        verbose_name_plural = 'Tarefas de Limpeza/Manutenção'
        ordering = ['-data_agendamento', 'status']
    
    def __str__(self):
        return f'{self.get_tipo_display()} do {self.quarto} - {self.get_status_display()}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para atualizar o status do quarto quando uma tarefa 
        é iniciada ou concluída e registrar a atividade no log.
        """
        is_new = self.pk is None
        status_anterior = None
        
        # Se não é novo, busca o objeto original para comparar status
        if not is_new:
            try:
                status_anterior = LimpezaManutencao.objects.get(pk=self.pk).status
            except:
                pass
        
        # Atualizações ao iniciar ou concluir tarefa
        if status_anterior != self.status:
            # Tarefa iniciada
            if self.status == 'em_andamento' and not self.data_inicio:
                self.data_inicio = timezone.now()
                
                # Atualiza status do quarto
                if self.tipo == 'limpeza':
                    self.quarto.status = 'limpeza'
                    self.quarto.save(update_fields=['status'])
                elif self.tipo in ['manutencao', 'reparo']:
                    self.quarto.status = 'manutencao'
                    self.quarto.save(update_fields=['status'])
                    
            # Tarefa concluída
            elif self.status == 'concluida' and not self.data_conclusao:
                self.data_conclusao = timezone.now()
                
                # Atualiza status do quarto e registra data da limpeza
                if self.tipo == 'limpeza':
                    self.quarto.status = 'disponivel'
                    self.quarto.ultima_limpeza = timezone.now()
                    self.quarto.save(update_fields=['status', 'ultima_limpeza'])
                elif self.tipo in ['manutencao', 'reparo'] and self.aprovado:
                    self.quarto.status = 'disponivel'
                    self.quarto.save(update_fields=['status'])
        
        super().save(*args, **kwargs)
        
        # Registra atividade no log
        if is_new:
            logger.info(f'Nova tarefa de {self.get_tipo_display()} registrada para {self.quarto}')
        else:
            if status_anterior != self.status:
                logger.info(f'Tarefa de {self.get_tipo_display()} para {self.quarto} alterada para {self.get_status_display()}')
            if self.status == 'concluida':
                logger.info(f'Tarefa de {self.get_tipo_display()} para {self.quarto} concluída por {self.responsavel}')


class ChecklistLimpeza(models.Model):
    """
    Modelo para gerenciar o checklist de limpeza dos quartos.
    Cada item representa uma tarefa específica a ser realizada durante a limpeza.
    """
    tarefa = models.ForeignKey(LimpezaManutencao, on_delete=models.CASCADE, related_name='itens_checklist')
    item = models.CharField(max_length=100)
    concluido = models.BooleanField(default=False)
    observacao = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Item do Checklist'
        verbose_name_plural = 'Itens do Checklist'
        ordering = ['id']
    
    def __str__(self):
        return f'{self.item} - {"Concluído" if self.concluido else "Pendente"}'
