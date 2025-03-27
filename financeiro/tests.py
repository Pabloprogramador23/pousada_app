from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import json

from reservas.models import Reserva, Historico
from financeiro.models import Pagamento, Receita
from quartos.models import Quarto, Categoria
from hospedes.models import Hospede


class PagamentoTestCase(TestCase):
    """
    Testes para o sistema de pagamentos e integração entre módulos.
    """
    
    def setUp(self):
        """
        Configura dados iniciais para os testes.
        """
        # Cria um usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
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
        
        # Cria uma reserva
        self.reserva = Reserva.objects.create(
            quarto=self.quarto,
            hospede=self.hospede,
            check_in=timezone.now().date(),
            check_out=timezone.now().date() + timezone.timedelta(days=2),
            adultos=2,
            criancas=0,
            valor_diaria=Decimal('140.00'),
            valor_total=Decimal('280.00'),
            status='confirmada',
            codigo='RES12345'
        )
        
        # Cliente para requisições
        self.client = Client()
    
    def test_permite_pagamento(self):
        """
        Testa o método permite_pagamento do modelo Reserva.
        """
        self.assertTrue(self.reserva.permite_pagamento())
        
        # Muda o status para concluída e verifica que não permite mais pagamento
        self.reserva.status = 'concluida'
        self.reserva.save()
        self.assertFalse(self.reserva.permite_pagamento())
    
    def test_get_saldo_pendente(self):
        """
        Testa o cálculo do saldo pendente.
        """
        # Inicialmente, o saldo pendente deve ser igual ao valor total
        self.assertEqual(self.reserva.get_saldo_pendente(), float(self.reserva.valor_total))
        
        # Cria um pagamento
        pagamento = Pagamento.objects.create(
            reserva=self.reserva,
            valor=Decimal('100.00'),
            tipo='dinheiro',
            status='aprovado',
            data_pagamento=timezone.now()
        )
        
        # Verifica se o saldo pendente foi atualizado corretamente
        self.assertEqual(self.reserva.get_saldo_pendente(), float(self.reserva.valor_total) - 100.00)
    
    def test_registrar_pagamento_ajax(self):
        """
        Testa a funcionalidade de registro de pagamento via AJAX.
        """
        # Faz login
        self.client.login(username='testuser', password='testpassword')
        
        # Dados para o pagamento
        data = {
            'codigo_reserva': self.reserva.codigo,
            'valor': 150.00,
            'forma_pagamento': 'dinheiro',
            'observacoes': 'Teste automatizado'
        }
        
        # Faz a requisição AJAX
        response = self.client.post(
            reverse('registrar_pagamento_ajax'),
            json.dumps(data),
            content_type='application/json'
        )
        
        # Verifica se a resposta foi bem-sucedida
        self.assertEqual(response.status_code, 200)
        
        # Verifica se o pagamento foi registrado
        self.assertEqual(Pagamento.objects.filter(reserva=self.reserva).count(), 1)
        
        # Verifica se a receita foi criada
        self.assertEqual(Receita.objects.filter(valor=Decimal('150.00')).count(), 1)
        
        # Verifica se o histórico foi criado
        self.assertEqual(
            Historico.objects.filter(
                reserva=self.reserva,
                descricao__contains='Pagamento de R$ 150.00'
            ).count(),
            1
        )
        
        # Verifica o saldo pendente atualizado
        response_data = json.loads(response.content)
        self.assertEqual(response_data['dados']['total_pago'], 150.00)
        self.assertEqual(response_data['dados']['valor_restante'], 130.00)
    
    def test_valor_pagamento_excede_pendente(self):
        """
        Testa a validação que impede pagamentos maiores que o valor pendente.
        """
        # Faz login
        self.client.login(username='testuser', password='testpassword')
        
        # Dados para o pagamento (valor maior que o total da reserva)
        data = {
            'codigo_reserva': self.reserva.codigo,
            'valor': 300.00,  # Maior que o valor total (280.00)
            'forma_pagamento': 'dinheiro',
            'observacoes': 'Teste automatizado'
        }
        
        # Faz a requisição AJAX
        response = self.client.post(
            reverse('registrar_pagamento_ajax'),
            json.dumps(data),
            content_type='application/json'
        )
        
        # Verifica se a resposta indica erro
        self.assertEqual(response.status_code, 400)
        
        # Verifica a mensagem de erro
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('excede o valor pendente', response_data['message'])
        
        # Verifica que nenhum pagamento foi registrado
        self.assertEqual(Pagamento.objects.filter(reserva=self.reserva).count(), 0)
