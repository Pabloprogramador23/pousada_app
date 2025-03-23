from django.db import models
import logging

logger = logging.getLogger(__name__)

class Banner(models.Model):
    """
    Modelo para banners da página inicial do site.
    Permite adicionar banners com link e texto.
    """
    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=200, blank=True, null=True)
    imagem = models.ImageField(upload_to='banners/')
    
    link = models.URLField(blank=True, null=True)
    texto_botao = models.CharField(max_length=30, blank=True, null=True)
    
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['ordem']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando um banner é criado ou atualizado.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo banner criado: {self.titulo}')
        else:
            logger.info(f'Banner atualizado: {self.titulo}')


class PaginaConteudo(models.Model):
    """
    Modelo para páginas de conteúdo do site.
    Permite criar páginas como Sobre, Contato, Políticas, etc.
    """
    TIPO_CHOICES = [
        ('sobre', 'Sobre Nós'),
        ('estrutura', 'Nossa Estrutura'),
        ('contato', 'Contato'),
        ('localizacao', 'Localização'),
        ('politica', 'Política de Privacidade'),
        ('termos', 'Termos de Uso'),
        ('faq', 'Perguntas Frequentes'),
        ('regras', 'Regras da Pousada'),
        ('outros', 'Outros'),
    ]
    
    titulo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    slug = models.SlugField(unique=True)
    
    conteudo = models.TextField()
    imagem_destaque = models.ImageField(upload_to='paginas/', blank=True, null=True)
    
    meta_descricao = models.CharField(max_length=160, blank=True, null=True, help_text='Descrição para SEO')
    
    ativo = models.BooleanField(default=True)
    ordem_menu = models.IntegerField(default=0)
    mostrar_no_menu = models.BooleanField(default=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Página de Conteúdo'
        verbose_name_plural = 'Páginas de Conteúdo'
        ordering = ['ordem_menu']
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando uma página é criada ou atualizada.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Nova página de conteúdo criada: {self.titulo}')
        else:
            logger.info(f'Página de conteúdo atualizada: {self.titulo}')


class Contato(models.Model):
    """
    Modelo para armazenar mensagens de contato enviadas pelo site.
    """
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    assunto = models.CharField(max_length=100)
    mensagem = models.TextField()
    
    data_envio = models.DateTimeField(auto_now_add=True)
    lido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['-data_envio']
    
    def __str__(self):
        return f'Contato de {self.nome} - {self.assunto}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando um contato é criado ou atualizado.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo contato recebido de {self.nome}: {self.assunto}')
        else:
            status = 'respondido' if self.respondido else 'lido' if self.lido else 'atualizado'
            logger.info(f'Contato de {self.nome} marcado como {status}')
