# Generated by Django 5.1.7 on 2025-04-05 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospedes', '0001_initial'),
        ('quartos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('check_in', models.DateTimeField()),
                ('check_out', models.DateTimeField()),
                ('quantidade_hospedes', models.PositiveSmallIntegerField(default=1)),
                ('quantidade_adultos', models.PositiveSmallIntegerField(default=1)),
                ('quantidade_criancas', models.PositiveSmallIntegerField(default=0)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-show')], default='pendente', max_length=20, verbose_name='Status')),
                ('status_anterior', models.CharField(blank=True, editable=False, max_length=20, null=True)),
                ('origem', models.CharField(default='site', max_length=50)),
                ('confirmada', models.BooleanField(default=False)),
                ('cancelada', models.BooleanField(default=False)),
                ('concluida', models.BooleanField(default=False)),
                ('no_show', models.BooleanField(default=False)),
                ('valor_diaria', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor da Diária')),
                ('valor_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor Total')),
                ('valor_sinal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('desconto_diaria', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Desconto na Diária')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('observacoes_admin', models.TextField(blank=True, null=True, verbose_name='Observações Administrativas')),
                ('solicitacoes_especiais', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('data_confirmacao', models.DateTimeField(blank=True, null=True)),
                ('data_cancelamento', models.DateTimeField(blank=True, null=True)),
                ('hospede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='hospedes.hospede', verbose_name='Hóspede')),
                ('quarto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='quartos.quarto', verbose_name='Quarto')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['-check_in'],
            },
        ),
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField(auto_now_add=True)),
                ('status_anterior', models.CharField(blank=True, choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-show')], max_length=15, null=True)),
                ('status_novo', models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-show')], max_length=15)),
                ('descricao', models.TextField()),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historicos', to='reservas.reserva')),
            ],
            options={
                'verbose_name': 'Histórico de Reserva',
                'verbose_name_plural': 'Históricos de Reservas',
                'ordering': ['-data_hora'],
            },
        ),
        migrations.AddConstraint(
            model_name='reserva',
            constraint=models.CheckConstraint(condition=models.Q(('check_out__gt', models.F('check_in'))), name='check_out_depois_do_check_in'),
        ),
    ]
