#!/usr/bin/env python
"""
Script para gerar dados de teste na Pousada Pajeú.
Cria quartos, hóspedes, reservas, pagamentos, receitas e despesas.
"""
import os
import sys
import random
import decimal
from datetime import datetime, timedelta, date
from decimal import Decimal

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pousada_app.settings')
import django
django.setup()

# Importa os modelos que vamos usar
from django.utils import timezone
from quartos.models import CategoriaQuarto, Quarto
from hospedes.models import Hospede
from reservas.models import Reserva, Historico
from financeiro.models import Pagamento, Despesa, Receita

# Listas para criação de dados aleatórios
NOMES = [
    "João Silva", "Maria Santos", "Pedro Almeida", "Ana Oliveira", "Carlos Souza",
    "Juliana Costa", "Roberto Pereira", "Camila Fernandes", "Lucas Ribeiro", "Aline Gomes",
    "Bruno Cardoso", "Daniela Martins", "Fábio Lima", "Patrícia Rodrigues", "Fernando Carvalho",
    "Cristina Ferreira", "Marcos Barbosa", "Letícia Andrade", "Gabriel Castro", "Beatriz Mendes"
]

EMAILS = [nome.lower().replace(" ", ".") + "@email.com" for nome in NOMES]

TELEFONES = [
    "(81) 98765-4321", "(81) 99876-5432", "(87) 98765-1234", "(87) 99887-7665",
    "(83) 98888-7777", "(83) 99999-8888", "(85) 98776-6655", "(85) 99887-7665",
    "(11) 98765-4321", "(11) 99999-8888", "(21) 98877-6655", "(21) 99887-7665",
    "(31) 98765-1234", "(31) 99876-5432", "(41) 98888-7777", "(41) 99999-8888",
    "(51) 98776-6655", "(51) 99887-7665", "(61) 98765-4321", "(61) 99999-8888"
]

CPFS = [
    "111.222.333-44", "222.333.444-55", "333.444.555-66", "444.555.666-77",
    "555.666.777-88", "666.777.888-99", "777.888.999-00", "888.999.000-11",
    "999.000.111-22", "000.111.222-33", "123.456.789-10", "234.567.890-12",
    "345.678.901-23", "456.789.012-34", "567.890.123-45", "678.901.234-56",
    "789.012.345-67", "890.123.456-78", "901.234.567-89", "012.345.678-90"
]

CATEGORIAS_QUARTO = [
    {"nome": "Standard", "descricao": "Quarto simples e confortável", "preco_base": 140.00, "capacidade": 2},
    {"nome": "Superior", "descricao": "Quarto espaçoso com vista para o jardim", "preco_base": 180.00, "capacidade": 2},
    {"nome": "Deluxe", "descricao": "Quarto amplo com sacada", "preco_base": 220.00, "capacidade": 3},
    {"nome": "Master", "descricao": "Quarto luxuoso com hidromassagem", "preco_base": 280.00, "capacidade": 4},
    {"nome": "Familiar", "descricao": "Quarto espaçoso ideal para famílias", "preco_base": 250.00, "capacidade": 5}
]

TIPOS_DESPESA = [
    "Limpeza", "Manutenção", "Alimentação", "Material de Escritório", "Água", 
    "Energia", "Internet", "Salários", "Impostos", "Marketing", "Compras"
]

TIPOS_RECEITA = [
    "Hospedagem", "Eventos", "Restaurante", "Bar", "Passeios", 
    "Lavanderia", "Spa", "Estacionamento", "Loja de Conveniência", "Outros"
]

# Formas de pagamento
FORMAS_PAGAMENTO = [escolha[0] for escolha in Pagamento.TIPO_CHOICES]

def criar_categorias_quarto():
    """Cria categorias de quarto."""
    print("Criando categorias de quarto...")
    
    for categoria_data in CATEGORIAS_QUARTO:
        CategoriaQuarto.objects.get_or_create(
            nome=categoria_data["nome"],
            defaults={
                "descricao": categoria_data["descricao"],
                "preco_base": categoria_data["preco_base"],
                "capacidade": categoria_data["capacidade"]
            }
        )
    
    return CategoriaQuarto.objects.all()

def criar_quartos(categorias):
    """Cria quartos com base nas categorias."""
    print("Criando quartos...")
    
    quartos_criados = []
    
    # Primeiro, criamos quartos Standard
    categoria_standard = CategoriaQuarto.objects.get(nome="Standard")
    for i in range(101, 111):
        quarto, created = Quarto.objects.get_or_create(
            numero=str(i),
            defaults={
                "categoria": categoria_standard,
                "descricao": f"Quarto Standard {i}",
                "capacidade": categoria_standard.capacidade,
                "preco_diaria": categoria_standard.preco_base,
                "tipo": "standard",
                "andar": "1",
                "status": "disponivel",
                "area": 18.0 + random.uniform(0, 4),
                "tem_ar_condicionado": True,
                "tem_tv": True,
                "tem_frigobar": True,
                "tem_wifi": True,
                "tem_varanda": False,
                "tem_banheira": False,
            }
        )
        quartos_criados.append(quarto)
    
    # Depois, criamos quartos Superior
    categoria_superior = CategoriaQuarto.objects.get(nome="Superior")
    for i in range(201, 211):
        quarto, created = Quarto.objects.get_or_create(
            numero=str(i),
            defaults={
                "categoria": categoria_superior,
                "descricao": f"Quarto Superior {i}",
                "capacidade": categoria_superior.capacidade,
                "preco_diaria": categoria_superior.preco_base,
                "tipo": "superior",
                "andar": "2",
                "status": "disponivel",
                "area": 22.0 + random.uniform(0, 4),
                "tem_ar_condicionado": True,
                "tem_tv": True,
                "tem_frigobar": True,
                "tem_wifi": True,
                "tem_varanda": True,
                "tem_banheira": False,
            }
        )
        quartos_criados.append(quarto)
    
    # Deluxe
    categoria_deluxe = CategoriaQuarto.objects.get(nome="Deluxe")
    for i in range(301, 306):
        quarto, created = Quarto.objects.get_or_create(
            numero=str(i),
            defaults={
                "categoria": categoria_deluxe,
                "descricao": f"Quarto Deluxe {i}",
                "capacidade": categoria_deluxe.capacidade,
                "preco_diaria": categoria_deluxe.preco_base,
                "tipo": "deluxe",
                "andar": "3",
                "status": "disponivel",
                "area": 25.0 + random.uniform(0, 5),
                "tem_ar_condicionado": True,
                "tem_tv": True,
                "tem_frigobar": True,
                "tem_wifi": True,
                "tem_varanda": True,
                "tem_banheira": False,
            }
        )
        quartos_criados.append(quarto)
    
    # Master
    categoria_master = CategoriaQuarto.objects.get(nome="Master")
    for i in range(401, 404):
        quarto, created = Quarto.objects.get_or_create(
            numero=str(i),
            defaults={
                "categoria": categoria_master,
                "descricao": f"Quarto Master {i}",
                "capacidade": categoria_master.capacidade,
                "preco_diaria": categoria_master.preco_base,
                "tipo": "master",
                "andar": "4",
                "status": "disponivel",
                "area": 30.0 + random.uniform(0, 8),
                "tem_ar_condicionado": True,
                "tem_tv": True,
                "tem_frigobar": True,
                "tem_wifi": True,
                "tem_varanda": True,
                "tem_banheira": True,
            }
        )
        quartos_criados.append(quarto)
    
    # Familiar
    categoria_familiar = CategoriaQuarto.objects.get(nome="Familiar")
    for i in range(501, 503):
        quarto, created = Quarto.objects.get_or_create(
            numero=str(i),
            defaults={
                "categoria": categoria_familiar,
                "descricao": f"Quarto Familiar {i}",
                "capacidade": categoria_familiar.capacidade,
                "preco_diaria": categoria_familiar.preco_base,
                "tipo": "master",
                "andar": "5",
                "status": "disponivel",
                "area": 35.0 + random.uniform(0, 5),
                "tem_ar_condicionado": True,
                "tem_tv": True,
                "tem_frigobar": True,
                "tem_wifi": True,
                "tem_varanda": True,
                "tem_banheira": True,
            }
        )
        quartos_criados.append(quarto)
    
    return quartos_criados

def criar_hospedes():
    """Cria hóspedes para testes."""
    print("Criando hóspedes...")
    
    hospedes_criados = []
    
    for i in range(min(len(NOMES), len(EMAILS), len(TELEFONES), len(CPFS))):
        data_nascimento = date.today() - timedelta(days=random.randint(8000, 25000))
        hospede, created = Hospede.objects.get_or_create(
            documento=CPFS[i].replace(".", "").replace("-", ""),
            tipo_documento="cpf",
            defaults={
                "nome": NOMES[i],
                "email": EMAILS[i],
                "telefone": TELEFONES[i],
                "data_nascimento": data_nascimento,
                "estado_civil": random.choice(["solteiro", "casado", "divorciado", "viuvo"]),
                "endereco": f"Rua das Flores, {random.randint(1, 999)}",
                "bairro": "Centro",
                "cidade": "Recife",
                "estado": "PE",
                "cep": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                "vip": random.choice([True, False, False, False])  # 25% de chance de ser VIP
            }
        )
        hospedes_criados.append(hospede)
    
    return hospedes_criados

def criar_reservas(quartos, hospedes, quantidade=30):
    """Cria reservas aleatórias para testes."""
    print(f"Criando {quantidade} reservas...")
    
    reservas_criadas = []
    hoje = timezone.now().date()
    
    # Status possíveis para reservas
    status_choices = ['pendente', 'confirmada', 'cancelada', 'concluida', 'no_show']
    status_weights = [0.15, 0.40, 0.15, 0.25, 0.05]  # Probabilidades para cada status
    
    # Cria reservas com diferentes datas de check-in e check-out
    for _ in range(quantidade):
        # Seleciona um quarto e um hóspede aleatoriamente
        quarto = random.choice(quartos)
        hospede = random.choice(hospedes)
        
        # Define datas de check-in e check-out
        # 1/3 das reservas no passado, 1/3 hoje e futuro próximo, 1/3 em futuro mais distante
        dias_offset = random.choice([
            random.randint(-60, -1),  # Passado
            random.randint(0, 30),    # Hoje e futuro próximo
            random.randint(31, 90)    # Futuro mais distante
        ])
        
        check_in_date = hoje + timedelta(days=dias_offset)
        duracao_estadia = random.randint(1, 7)  # Entre 1 e 7 dias
        check_out_date = check_in_date + timedelta(days=duracao_estadia)
        
        # Hora aleatória para check-in e check-out
        check_in_hora = datetime.combine(check_in_date, datetime.min.time().replace(hour=14, minute=random.randint(0, 59)))
        check_out_hora = datetime.combine(check_out_date, datetime.min.time().replace(hour=12, minute=random.randint(0, 59)))
        
        # Converte para aware datetime
        check_in = timezone.make_aware(check_in_hora)
        check_out = timezone.make_aware(check_out_hora)
        
        # Define quantidade de hóspedes
        quantidade_adultos = random.randint(1, quarto.capacidade - 1)
        quantidade_criancas = random.randint(0, min(3, quarto.capacidade - quantidade_adultos))
        quantidade_hospedes = quantidade_adultos + quantidade_criancas
        
        # Define status baseado nas probabilidades
        status = random.choices(status_choices, weights=status_weights, k=1)[0]
        
        # Ajusta status baseado na data (lógica de negócio)
        if check_out_date < hoje and status in ['pendente', 'confirmada']:
            status = random.choice(['concluida', 'no_show'])
        elif check_in_date > hoje and status in ['concluida', 'no_show']:
            status = random.choice(['pendente', 'confirmada', 'cancelada'])
        
        # Calcula valores
        valor_diaria = Decimal(str(quarto.preco_diaria))
        desconto = Decimal('0.00')
        if random.random() < 0.2:  # 20% de chance de ter desconto
            desconto = Decimal(str(random.randint(5, 20))) / Decimal('100')
        
        valor_com_desconto = valor_diaria * (Decimal('1.00') - desconto)
        valor_total = valor_com_desconto * Decimal(str(duracao_estadia))
        
        # Cria a reserva
        try:
            reserva = Reserva.objects.create(
                codigo=f'RES{check_in_date.strftime("%y%m%d")}{random.randint(1000, 9999)}',
                quarto=quarto,
                hospede=hospede,
                check_in=check_in,
                check_out=check_out,
                quantidade_hospedes=quantidade_hospedes,
                quantidade_adultos=quantidade_adultos,
                quantidade_criancas=quantidade_criancas,
                status=status,
                origem=random.choice(['site', 'telefone', 'presencial', 'booking', 'airbnb']),
                valor_diaria=valor_com_desconto,
                valor_total=valor_total,
                desconto_diaria=valor_diaria * desconto,
                observacoes=f"Reserva de teste criada automaticamente para {hospede.nome}."
            )
            
            # Adiciona histórico para reservas não pendentes
            if status != 'pendente':
                data_alteracao = timezone.now() - timedelta(days=random.randint(1, 7))
                Historico.objects.create(
                    reserva=reserva,
                    status_anterior='pendente',
                    status_novo=status,
                    data_hora=data_alteracao,
                    descricao=f"Status alterado de pendente para {status}."
                )
            
            reservas_criadas.append(reserva)
            print(f"Reserva {reserva.codigo} criada com sucesso.")
            
        except Exception as e:
            print(f"Erro ao criar reserva: {e}")
    
    return reservas_criadas

def criar_pagamentos(reservas):
    """Cria pagamentos para as reservas confirmadas ou concluídas."""
    print("Criando pagamentos...")
    
    pagamentos_criados = []
    
    for reserva in reservas:
        # Só cria pagamentos para reservas confirmadas ou concluídas
        if reserva.status in ['confirmada', 'concluida']:
            # Decide quantos pagamentos para esta reserva
            num_pagamentos = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05], k=1)[0]
            
            valor_total = reserva.valor_total
            valor_ja_pago = Decimal('0.00')
            
            for i in range(num_pagamentos):
                # Define o valor do pagamento
                if i == num_pagamentos - 1:  # Último pagamento
                    valor = valor_total - valor_ja_pago
                else:
                    # Primeiro pagamento = 30-50% do total, segundo = 20-40% do total
                    percentual = Decimal(str(random.randint(30 if i == 0 else 20, 50 if i == 0 else 40))) / Decimal('100')
                    valor = valor_total * percentual
                    valor_ja_pago += valor
                
                # Define a data do pagamento
                if reserva.status == 'confirmada':
                    # Pagamentos entre a criação e hoje
                    dias_aleatorios = random.randint(0, max(1, (timezone.now().date() - reserva.data_criacao.date()).days))
                    data_pagamento = reserva.data_criacao + timedelta(days=dias_aleatorios)
                else:  # Concluída
                    # Pagamentos entre a criação e o check-out
                    dias_aleatorios = random.randint(0, max(1, (reserva.check_out.date() - reserva.data_criacao.date()).days))
                    data_pagamento = reserva.data_criacao + timedelta(days=dias_aleatorios)
                
                # Cria o pagamento
                tipo_pagamento = random.choice(FORMAS_PAGAMENTO)
                status_pagamento = 'aprovado' if random.random() < 0.9 else 'pendente'  # 90% aprovado, 10% pendente
                
                pagamento = Pagamento.objects.create(
                    reserva=reserva,
                    valor=valor,
                    tipo=tipo_pagamento,
                    status=status_pagamento,
                    data_pagamento=data_pagamento,
                    codigo_transacao=f"TX-{random.randint(100000, 999999)}",
                    observacoes=f"Pagamento {i+1}/{num_pagamentos} - {tipo_pagamento.replace('_', ' ').title()}"
                )
                
                pagamentos_criados.append(pagamento)
    
    return pagamentos_criados

def criar_despesas(quantidade=50):
    """Cria despesas aleatórias para a pousada."""
    print(f"Criando {quantidade} despesas...")
    
    despesas_criadas = []
    hoje = timezone.now().date()
    
    for _ in range(quantidade):
        # Define data da despesa (entre 6 meses atrás e 2 meses à frente)
        dias_aleatorios = random.randint(-180, 60)
        data_despesa = hoje + timedelta(days=dias_aleatorios)
        data_vencimento = data_despesa + timedelta(days=random.randint(5, 15))
        
        # Define valor entre R$ 50 e R$ 5000
        valor = Decimal(str(random.uniform(50, 5000))).quantize(Decimal('0.01'))
        
        # Define categoria e status
        categoria = random.choice(['manutencao', 'limpeza', 'alimentacao', 'energia', 'agua', 'internet', 'funcionarios', 'impostos', 'marketing', 'outros'])
        
        # Define o status
        if data_vencimento < hoje:
            status = 'pago' if random.random() < 0.9 else 'atrasado'  # 90% pago, 10% atrasado
        else:
            status = 'pendente'
        
        # Data de pagamento (somente se estiver pago)
        data_pagamento = None
        if status == 'pago':
            dias_ate_pagamento = random.randint(0, 5)
            data_pagamento = min(hoje, data_vencimento + timedelta(days=dias_ate_pagamento))
        
        # Cria a despesa
        despesa = Despesa.objects.create(
            descricao=f"Despesa com {dict(Despesa.CATEGORIA_CHOICES).get(categoria, categoria)} - {random.randint(1000, 9999)}",
            valor=valor,
            data_despesa=data_despesa,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            categoria=categoria,
            status=status,
            observacoes=f"Despesa de teste gerada automaticamente para {dict(Despesa.CATEGORIA_CHOICES).get(categoria, categoria)}."
        )
        
        despesas_criadas.append(despesa)
    
    return despesas_criadas

def criar_receitas(quantidade=30):
    """Cria receitas aleatórias não relacionadas a reservas."""
    print(f"Criando {quantidade} receitas extras...")
    
    receitas_criadas = []
    hoje = timezone.now().date()
    
    for _ in range(quantidade):
        # Define data da receita (entre 6 meses atrás e 2 meses à frente)
        dias_aleatorios = random.randint(-180, 60)
        data_receita = hoje + timedelta(days=dias_aleatorios)
        
        # Define valor entre R$ 20 e R$ 2000
        valor = Decimal(str(random.uniform(20, 2000))).quantize(Decimal('0.01'))
        
        # Define categoria
        categoria = random.choice(['hospedagem', 'aluguel', 'freela', 'eventos', 'produtos', 'outros'])
        
        # Define o status
        if data_receita < hoje:
            status = 'recebido' if random.random() < 0.9 else 'atrasado'  # 90% recebido, 10% atrasado
        else:
            status = 'pendente'
        
        # Data de recebimento (somente se estiver recebido)
        data_recebimento = None
        if status == 'recebido':
            data_recebimento = data_receita
        
        # Recorrência - 20% de chance de ser recorrente
        recorrente = random.random() < 0.2
        
        # Cria a receita
        receita = Receita.objects.create(
            descricao=f"Receita com {dict(Receita.CATEGORIA_CHOICES).get(categoria, categoria)} - {random.randint(1000, 9999)}",
            valor=valor,
            data_receita=data_receita,
            data_recebimento=data_recebimento,
            categoria=categoria,
            status=status,
            recorrente=recorrente,
            observacoes=f"Receita de teste gerada automaticamente para {dict(Receita.CATEGORIA_CHOICES).get(categoria, categoria)}."
        )
        
        receitas_criadas.append(receita)
    
    return receitas_criadas

def main():
    """Função principal que executa a criação de dados de teste."""
    print("=== Iniciando criação de dados de teste ===")
    
    # Cria categorias de quarto e quartos
    categorias = criar_categorias_quarto()
    quartos = criar_quartos(categorias)
    
    # Cria hóspedes
    hospedes = criar_hospedes()
    
    # Cria reservas
    reservas = criar_reservas(quartos, hospedes, 50)
    
    # Cria pagamentos para reservas
    pagamentos = criar_pagamentos(reservas)
    
    # Cria despesas
    despesas = criar_despesas(80)
    
    # Cria receitas extras
    receitas = criar_receitas(40)
    
    print("=== Dados de teste criados com sucesso! ===")
    
    # Resumo
    print(f"\nResumo dos dados criados:")
    print(f"- {len(categorias)} categorias de quarto")
    print(f"- {len(quartos)} quartos")
    print(f"- {len(hospedes)} hóspedes")
    print(f"- {len(reservas)} reservas")
    print(f"- {len(pagamentos)} pagamentos")
    print(f"- {len(despesas)} despesas")
    print(f"- {len(receitas)} receitas")

if __name__ == "__main__":
    main() 