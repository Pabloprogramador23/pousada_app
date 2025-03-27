# Generated by Django 5.1.7 on 2025-03-26 21:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('mensagem', models.TextField()),
                ('tipo', models.CharField(choices=[('info', 'Informação'), ('success', 'Sucesso'), ('warning', 'Aviso'), ('danger', 'Alerta')], default='info', max_length=10)),
                ('categoria', models.CharField(choices=[('reserva', 'Reserva'), ('pagamento', 'Pagamento'), ('hospede', 'Hóspede'), ('quarto', 'Quarto'), ('sistema', 'Sistema')], default='sistema', max_length=20)),
                ('lida', models.BooleanField(default=False)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('url_acao', models.CharField(blank=True, max_length=255, null=True)),
                ('texto_acao', models.CharField(blank=True, max_length=50, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_criacao'],
            },
        ),
    ]
