from django.db import models
import logging

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
    
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quarto'
        verbose_name_plural = 'Quartos'
        ordering = ['numero']
    
    def __str__(self):
        return f'Quarto {self.numero} - {self.categoria.nome}'
    
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
        
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo quarto criado: {self.numero}')
        else:
            logger.info(f'Quarto atualizado: {self.numero}')


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
