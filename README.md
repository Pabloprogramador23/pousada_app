# Sistema de Gerenciamento - Pousada Pajeu

Sistema para gerenciamento de pousada desenvolvido com Django.

## Funcionalidades

- Gerenciamento de quartos
- Controle de reservas
- Cadastro de hóspedes
- Gestão financeira
- Site/landing page para clientes

## Requisitos

- Python 3.8+
- Django 5.1+
- python-dotenv

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Configure as variáveis de ambiente no arquivo `.env`
6. Execute as migrações: `python manage.py migrate`
7. Crie um superusuário: `python manage.py createsuperuser`
8. Inicie o servidor: `python manage.py runserver`

## Estrutura do Projeto

- `quartos`: Gerenciamento de quartos e categorias
- `reservas`: Controle de reservas e disponibilidade
- `hospedes`: Cadastro e gestão de hóspedes
- `financeiro`: Controle de pagamentos e relatórios
- `website`: Site/landing page para os clientes

## Desenvolvimento

Este projeto segue as boas práticas de desenvolvimento Python:
- Padrões PEP8 e Clean Code
- Documentação em português
- Utilização de logging para registros
- Variáveis de ambiente com python-dotenv 