# Generated by Django 5.1.7 on 2025-03-23 15:59

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
                ('codigo', models.CharField(blank=True, max_length=20, unique=True)),
                ('check_in', models.DateField(verbose_name='Data de Check-in')),
                ('check_out', models.DateField(verbose_name='Data de Check-out')),
                ('hora_checkin', models.TimeField(blank=True, null=True)),
                ('hora_checkout', models.TimeField(blank=True, null=True)),
                ('adultos', models.PositiveSmallIntegerField(default=2)),
                ('criancas', models.PositiveSmallIntegerField(default=0)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-Show')], default='pendente', max_length=20)),
                ('origem', models.CharField(default='site', max_length=50)),
                ('confirmada', models.BooleanField(default=False)),
                ('cancelada', models.BooleanField(default=False)),
                ('motivo_cancelamento', models.TextField(blank=True, null=True)),
                ('valor_diaria', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valor_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('valor_sinal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('observacoes_admin', models.TextField(blank=True, null=True, verbose_name='Observações Administrativas')),
                ('solicitacoes_especiais', models.TextField(blank=True, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('data_confirmacao', models.DateTimeField(blank=True, null=True)),
                ('data_cancelamento', models.DateTimeField(blank=True, null=True)),
                ('hospede', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='hospedes.hospede')),
                ('quarto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservas', to='quartos.quarto')),
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
                ('status_anterior', models.CharField(blank=True, choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-Show')], max_length=15, null=True)),
                ('status_novo', models.CharField(choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('concluida', 'Concluída'), ('no_show', 'No-Show')], max_length=15)),
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
            constraint=models.CheckConstraint(condition=models.Q(('check_in__lt', models.F('check_out'))), name='check_in_anterior_check_out'),
        ),
    ]
