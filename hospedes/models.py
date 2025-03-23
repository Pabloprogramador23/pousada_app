from django.db import models
from django.core.validators import RegexValidator
import logging

logger = logging.getLogger(__name__)

class Hospede(models.Model):
    """
    Modelo para cadastro e gerenciamento de hóspedes da pousada.
    Armazena informações pessoais e documentos.
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('cpf', 'CPF'),
        ('rg', 'RG'),
        ('passaporte', 'Passaporte'),
        ('cnh', 'CNH'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
        ('outros', 'Outros'),
    ]
    
    # Validador para telefones brasileiros
    telefone_validator = RegexValidator(
        regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
        message='O telefone deve estar no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX'
    )
    
    # Informações pessoais
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, validators=[telefone_validator])
    data_nascimento = models.DateField()
    estado_civil = models.CharField(max_length=15, choices=ESTADO_CIVIL_CHOICES, default='solteiro')
    
    # Documentos
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES)
    documento = models.CharField(max_length=20)
    
    # Endereço
    endereco = models.CharField(max_length=150)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    
    # Preferências e observações
    observacoes = models.TextField(blank=True, null=True)
    vip = models.BooleanField(default=False)
    
    # Controle
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ultima_hospedagem = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Hóspede'
        verbose_name_plural = 'Hóspedes'
        ordering = ['nome']
        unique_together = ['tipo_documento', 'documento']
    
    def __str__(self):
        return f'{self.nome} - {self.documento}'
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para registrar no log quando um hóspede é criado ou atualizado.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            logger.info(f'Novo hóspede cadastrado: {self.nome}')
        else:
            logger.info(f'Dados do hóspede atualizados: {self.nome}')


class Preferencia(models.Model):
    """
    Modelo para armazenar preferências específicas dos hóspedes.
    Permite personalizar a estadia conforme as preferências individuais.
    """
    hospede = models.ForeignKey(Hospede, on_delete=models.CASCADE, related_name='preferencias')
    categoria = models.CharField(max_length=50)
    descricao = models.TextField()
    
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Preferência'
        verbose_name_plural = 'Preferências'
        ordering = ['hospede', 'categoria']
    
    def __str__(self):
        return f'{self.hospede.nome} - {self.categoria}'
