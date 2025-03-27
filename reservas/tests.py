from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from reservas.models import Reserva, Historico
from quartos.models import Quarto, Categoria
from hospedes.models import Hospede


class ReservaModelTestCase(TestCase):
    """
    Testes para o modelo de Reserva.
    """
    
    def setUp(self):
        """
        Configura dados iniciais para os testes.
        """
        # Cria categoria e quarto
        self.categoria = Categoria.objects.create(
            nome='Standard',
            descricao='Quarto padrão'
        )
        
        self.quarto = Quarto.objects.create(
            numero='101',
            categoria=self.categoria,
            capacidade=3,
            camas_casal=1,
            camas_solteiro=1,
            preco_diaria=Decimal('140.00'),
            status='disponivel'
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
        
        # Cria uma reserva
        self.reserva = Reserva.objects.create(
            quarto=self.quarto,
            hospede=self.hospede,
            check_in=self.hoje,
            check_out=self.hoje + timedelta(days=2),
            adultos=2,
            criancas=0,
            valor_diaria=Decimal('140.00'),
            valor_total=Decimal('280.00'),
            status='confirmada',
            codigo='RES12345'
        )
    
    def test_calcular_total(self):
        """
        Testa o método de cálculo do valor total da reserva.
        """
        # Atualiza para testar o cálculo
        self.reserva.adultos = 3  # Adiciona um adulto extra
        self.reserva.check_in = self.hoje
        self.reserva.check_out = self.hoje + timedelta(days=3)  # 3 diárias
        
        # Recalcula o total
        total = self.reserva.calcular_total()
        
        # Deve ser: R$140 base + R$70 por pessoa extra = R$210 por dia * 3 dias = R$630
        self.assertEqual(total, Decimal('630.00'))
    
    def test_calculo_com_desconto(self):
        """
        Testa o cálculo do valor com desconto por diária.
        """
        # Define um desconto de R$20 por diária
        self.reserva.desconto_diaria = Decimal('20.00')
        self.reserva.check_in = self.hoje
        self.reserva.check_out = self.hoje + timedelta(days=2)  # 2 diárias
        
        # Recalcula o total
        total = self.reserva.calcular_total()
        
        # Deve ser: (R$140 - R$20) * 2 dias = R$240
        self.assertEqual(total, Decimal('240.00'))
    
    def test_valor_minimo_diaria_com_desconto(self):
        """
        Testa o valor mínimo da diária mesmo com descontos altos.
        """
        # Define um desconto de R$50 por diária (que levaria a diária abaixo do mínimo)
        self.reserva.desconto_diaria = Decimal('50.00')
        self.reserva.check_in = self.hoje
        self.reserva.check_out = self.hoje + timedelta(days=2)  # 2 diárias
        
        # Recalcula o total
        total = self.reserva.calcular_total()
        
        # Deve ser: R$100 (mínimo) * 2 dias = R$200
        self.assertEqual(total, Decimal('200.00'))
    
    def test_status_color(self):
        """
        Testa o método get_status_color.
        """
        # Testa status confirmada
        self.reserva.status = 'confirmada'
        self.assertEqual(self.reserva.get_status_color(), 'primary')
        
        # Testa status em_andamento
        self.reserva.status = 'em_andamento'
        self.assertEqual(self.reserva.get_status_color(), 'success')
        
        # Testa status cancelada
        self.reserva.status = 'cancelada'
        self.assertEqual(self.reserva.get_status_color(), 'danger')


class CheckInCheckOutTestCase(TestCase):
    """
    Testes para as funcionalidades de check-in e check-out.
    """
    
    def setUp(self):
        """
        Configura dados iniciais para os testes.
        """
        # Cria categoria e quarto
        self.categoria = Categoria.objects.create(
            nome='Standard',
            descricao='Quarto padrão'
        )
        
        self.quarto = Quarto.objects.create(
            numero='101',
            categoria=self.categoria,
            capacidade=2,
            camas_casal=1,
            camas_solteiro=0,
            preco_diaria=Decimal('140.00'),
            status='disponivel'
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
        
        # Cria uma reserva
        self.reserva = Reserva.objects.create(
            quarto=self.quarto,
            hospede=self.hospede,
            check_in=self.hoje,
            check_out=self.hoje + timedelta(days=2),
            adultos=2,
            criancas=0,
            valor_diaria=Decimal('140.00'),
            valor_total=Decimal('280.00'),
            status='confirmada',
            codigo='RES12345'
        )
        
        # Cliente para requisições
        self.client = Client()
    
    def test_realizar_check_in(self):
        """
        Testa a realização de check-in.
        """
        # Preparar dados para o check-in
        check_in_data = {
            'forma_pagamento': 'dinheiro',
            'valor_pago': '280.00',
            'desconto_diaria': '0.00'
        }
        
        # Fazer a requisição para realizar check-in
        response = self.client.post(
            reverse('realizar_check_in', args=[self.reserva.codigo]),
            check_in_data
        )
        
        # Recarga a reserva do banco de dados
        self.reserva.refresh_from_db()
        
        # Verifica se o status foi atualizado para 'em_andamento'
        self.assertEqual(self.reserva.status, 'em_andamento')
        
        # Verifica se existe registro no histórico
        self.assertTrue(
            Historico.objects.filter(
                reserva=self.reserva,
                status_novo='em_andamento'
            ).exists()
        )
        
        # Verifica se o quarto ficou marcado como ocupado
        self.quarto.refresh_from_db()
        self.assertEqual(self.quarto.status, 'ocupado')
    
    def test_check_in_direto(self):
        """
        Testa a realização de check-in direto (sem reserva prévia).
        """
        # Preparar dados para o check-in direto
        data = {
            'nome': 'Novo',
            'sobrenome': 'Cliente',
            'email': 'novo@example.com',
            'telefone': '8888888888',
            'cpf': '98765432100',
            'data_nascimento': self.hoje - timedelta(days=365*30),  # 30 anos atrás
            'quarto': self.quarto.id,
            'check_in': self.hoje.strftime('%Y-%m-%d'),
            'check_out': (self.hoje + timedelta(days=1)).strftime('%Y-%m-%d'),
            'adultos': 2,
            'criancas': 0,
            'valor_diaria': '140.00',
            'desconto_diaria': '0.00',
            'valor_pago': '140.00',
            'forma_pagamento': 'dinheiro',
            'observacoes': 'Check-in direto de teste'
        }
        
        # Fazer a requisição para realizar check-in direto
        response = self.client.post(reverse('check_in_direto'), data)
        
        # Verifica se uma nova reserva foi criada
        self.assertEqual(Reserva.objects.count(), 2)
        
        # Obtém a nova reserva
        nova_reserva = Reserva.objects.exclude(codigo=self.reserva.codigo).first()
        
        # Verifica os dados da nova reserva
        self.assertEqual(nova_reserva.quarto, self.quarto)
        self.assertEqual(nova_reserva.adultos, 2)
        self.assertEqual(nova_reserva.status, 'em_andamento')
        
        # Verifica se o quarto ficou marcado como ocupado
        self.quarto.refresh_from_db()
        self.assertEqual(self.quarto.status, 'ocupado')
