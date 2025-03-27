from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from quartos.models import Quarto, Categoria
from reservas.models import Reserva
from hospedes.models import Hospede


class QuartoModelTestCase(TestCase):
    """
    Testes para o modelo de Quarto.
    """
    
    def setUp(self):
        """
        Configura dados iniciais para os testes.
        """
        # Cria categorias de quartos
        self.categoria_standard = Categoria.objects.create(
            nome='Standard',
            descricao='Quarto padrão'
        )
        
        self.categoria_luxo = Categoria.objects.create(
            nome='Luxo',
            descricao='Quarto de luxo'
        )
        
        # Cria quartos
        self.quarto_standard = Quarto.objects.create(
            numero='101',
            categoria=self.categoria_standard,
            capacidade=2,
            camas_casal=1,
            camas_solteiro=0,
            preco_diaria=Decimal('140.00'),
            status='disponivel'
        )
        
        self.quarto_luxo = Quarto.objects.create(
            numero='201',
            categoria=self.categoria_luxo,
            capacidade=3,
            camas_casal=1,
            camas_solteiro=1,
            preco_diaria=Decimal('200.00'),
            status='disponivel'
        )
        
        self.quarto_ocupado = Quarto.objects.create(
            numero='102',
            categoria=self.categoria_standard,
            capacidade=2,
            camas_casal=1,
            camas_solteiro=0,
            preco_diaria=Decimal('140.00'),
            status='ocupado'
        )
        
        # Cria hóspede
        self.hospede = Hospede.objects.create(
            nome='Teste',
            sobrenome='da Silva',
            email='teste@example.com',
            telefone='8899999999',
            cpf='12345678900',
            data_nascimento=timezone.now().date()
        )
        
        # Data atual
        self.hoje = date.today()
        
        # Cria uma reserva para o quarto ocupado
        self.reserva = Reserva.objects.create(
            quarto=self.quarto_ocupado,
            hospede=self.hospede,
            check_in=self.hoje,
            check_out=self.hoje + timedelta(days=2),
            adultos=2,
            criancas=0,
            valor_diaria=Decimal('140.00'),
            valor_total=Decimal('280.00'),
            status='em_andamento',
            codigo='RES12345'
        )
    
    def test_get_preco_com_desconto(self):
        """
        Testa o cálculo do preço com desconto.
        """
        # Define um desconto no quarto e verifica o preço
        self.quarto_luxo.desconto_valor = Decimal('30.00')
        self.quarto_luxo.save()
        
        # Verifica o preço com desconto
        self.assertEqual(self.quarto_luxo.preco_com_desconto(), Decimal('170.00'))
        
        # Testa com desconto percentual
        self.quarto_luxo.desconto_valor = Decimal('0.00')
        self.quarto_luxo.desconto_percentual = 20  # 20%
        self.quarto_luxo.save()
        
        # Verifica o preço com desconto percentual (200 - 20% = 160)
        self.assertEqual(self.quarto_luxo.preco_com_desconto(), Decimal('160.00'))
    
    def test_verificar_disponibilidade(self):
        """
        Testa a verificação de disponibilidade de quartos.
        """
        # O quarto standard deve estar disponível
        self.assertTrue(self.quarto_standard.esta_disponivel(
            self.hoje + timedelta(days=3),  # Check-in após a reserva existente
            self.hoje + timedelta(days=5)
        ))
        
        # O quarto ocupado não deve estar disponível durante a reserva
        self.assertFalse(self.quarto_ocupado.esta_disponivel(
            self.hoje,
            self.hoje + timedelta(days=1)
        ))
        
        # Verifica sobreposição parcial (check-in durante uma reserva)
        self.assertFalse(self.quarto_ocupado.esta_disponivel(
            self.hoje + timedelta(days=1),  # Durante a reserva
            self.hoje + timedelta(days=3)   # Após a reserva
        ))
        
        # Verifica sobreposição total (reserva dentro de outra)
        self.assertFalse(self.quarto_ocupado.esta_disponivel(
            self.hoje - timedelta(days=1),  # Antes da reserva
            self.hoje + timedelta(days=3)   # Após a reserva
        ))
    
    def test_buscar_quartos_disponiveis(self):
        """
        Testa a busca de quartos disponíveis para um período.
        """
        # Busca quartos disponíveis no período após a reserva existente
        quartos_disponiveis = Quarto.buscar_disponiveis(
            check_in=self.hoje + timedelta(days=3),  # Após a reserva
            check_out=self.hoje + timedelta(days=5),
            capacidade=2
        )
        
        # Deve encontrar os dois quartos (standard e luxo)
        self.assertEqual(quartos_disponiveis.count(), 2)
        self.assertIn(self.quarto_standard, quartos_disponiveis)
        self.assertIn(self.quarto_luxo, quartos_disponiveis)
        
        # Busca durante o período da reserva
        quartos_disponiveis = Quarto.buscar_disponiveis(
            check_in=self.hoje,
            check_out=self.hoje + timedelta(days=1),
            capacidade=2
        )
        
        # Deve encontrar apenas o quarto standard
        self.assertEqual(quartos_disponiveis.count(), 1)
        self.assertIn(self.quarto_standard, quartos_disponiveis)
        self.assertNotIn(self.quarto_ocupado, quartos_disponiveis)
        
        # Busca para capacidade maior
        quartos_disponiveis = Quarto.buscar_disponiveis(
            check_in=self.hoje + timedelta(days=3),
            check_out=self.hoje + timedelta(days=5),
            capacidade=3  # Apenas o quarto de luxo comporta 3 pessoas
        )
        
        # Deve encontrar apenas o quarto de luxo
        self.assertEqual(quartos_disponiveis.count(), 1)
        self.assertIn(self.quarto_luxo, quartos_disponiveis)
    
    def test_modelo_str(self):
        """
        Testa a representação string dos modelos.
        """
        self.assertEqual(str(self.categoria_standard), 'Standard')
        self.assertEqual(str(self.quarto_standard), 'Quarto 101 - Standard')
    
    def test_preco_minimo(self):
        """
        Testa a aplicação do preço mínimo.
        """
        # Define um desconto grande que levaria o preço abaixo do mínimo
        self.quarto_standard.desconto_valor = Decimal('100.00')  # Desconto maior que o preço
        self.quarto_standard.save()
        
        # O preço não deve ficar abaixo do mínimo (geralmente R$100,00)
        self.assertEqual(self.quarto_standard.preco_com_desconto(), Decimal('100.00'))
