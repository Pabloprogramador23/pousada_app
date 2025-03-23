# Generated by Django 5.1.7 on 2025-03-23 15:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=200)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('categoria', models.CharField(choices=[('manutencao', 'Manutenção'), ('limpeza', 'Limpeza'), ('alimentacao', 'Alimentação'), ('energia', 'Energia Elétrica'), ('agua', 'Água'), ('internet', 'Internet'), ('funcionarios', 'Funcionários'), ('impostos', 'Impostos'), ('marketing', 'Marketing'), ('outros', 'Outros')], max_length=20)),
                ('data_despesa', models.DateField()),
                ('data_pagamento', models.DateField(blank=True, null=True)),
                ('comprovante', models.FileField(blank=True, null=True, upload_to='despesas/')),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Despesas',
                'ordering': ['-data_despesa'],
            },
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo', models.CharField(choices=[('dinheiro', 'Dinheiro'), ('cartao_credito', 'Cartão de Crédito'), ('cartao_debito', 'Cartão de Débito'), ('pix', 'PIX'), ('transferencia', 'Transferência Bancária'), ('deposito', 'Depósito Bancário'), ('outros', 'Outros')], max_length=20)),
                ('status', models.CharField(choices=[('aprovado', 'Aprovado'), ('pendente', 'Pendente'), ('recusado', 'Recusado'), ('estornado', 'Estornado')], default='pendente', max_length=15)),
                ('data_pagamento', models.DateTimeField(default=django.utils.timezone.now)),
                ('codigo_transacao', models.CharField(blank=True, max_length=50, null=True)),
                ('comprovante', models.FileField(blank=True, null=True, upload_to='comprovantes/')),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pagamentos', to='reservas.reserva')),
            ],
            options={
                'verbose_name': 'Pagamento',
                'verbose_name_plural': 'Pagamentos',
                'ordering': ['-data_pagamento'],
            },
        ),
    ]
