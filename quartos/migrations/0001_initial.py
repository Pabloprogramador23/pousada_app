# Generated by Django 5.1.7 on 2025-04-05 12:23

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaQuarto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('descricao', models.TextField()),
                ('preco_base', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacidade', models.PositiveSmallIntegerField(default=2)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Categoria de Quarto',
                'verbose_name_plural': 'Categorias de Quartos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='LimpezaManutencao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('limpeza', 'Limpeza'), ('manutencao', 'Manutenção'), ('vistoria', 'Vistoria'), ('reparo', 'Reparo')], max_length=15)),
                ('descricao', models.TextField()),
                ('prioridade', models.CharField(choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta'), ('urgente', 'Urgente')], default='media', max_length=10)),
                ('status', models.CharField(choices=[('agendada', 'Agendada'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='agendada', max_length=15)),
                ('data_agendamento', models.DateTimeField(default=django.utils.timezone.now)),
                ('data_inicio', models.DateTimeField(blank=True, null=True)),
                ('data_conclusao', models.DateTimeField(blank=True, null=True)),
                ('tempo_estimado', models.PositiveIntegerField(default=30, help_text='Tempo estimado em minutos')),
                ('responsavel', models.CharField(max_length=100)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('custo', models.DecimalField(decimal_places=2, default=0, help_text='Custo em R$', max_digits=10)),
                ('checklist_completo', models.BooleanField(default=False)),
                ('aprovado', models.BooleanField(default=False)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tarefa de Limpeza/Manutenção',
                'verbose_name_plural': 'Tarefas de Limpeza/Manutenção',
                'ordering': ['-data_agendamento', 'status'],
            },
        ),
        migrations.CreateModel(
            name='ChecklistLimpeza',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('concluido', models.BooleanField(default=False)),
                ('observacao', models.CharField(blank=True, max_length=200, null=True)),
                ('tarefa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_checklist', to='quartos.limpezamanutencao')),
            ],
            options={
                'verbose_name': 'Item do Checklist',
                'verbose_name_plural': 'Itens do Checklist',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Quarto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10, unique=True, verbose_name='Número')),
                ('andar', models.CharField(blank=True, max_length=10, null=True, verbose_name='Andar')),
                ('tipo', models.CharField(choices=[('standard', 'Standard'), ('superior', 'Superior'), ('master', 'Master'), ('deluxe', 'Deluxe')], default='standard', max_length=20, verbose_name='Tipo')),
                ('capacidade', models.PositiveSmallIntegerField(default=2, verbose_name='Capacidade')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('preco_base', models.DecimalField(decimal_places=2, default=140.0, max_digits=10, verbose_name='Preço Base')),
                ('status', models.CharField(choices=[('disponivel', 'Disponível'), ('ocupado', 'Ocupado'), ('manutencao', 'Manutenção'), ('limpeza', 'Em limpeza')], default='disponivel', max_length=20, verbose_name='Status')),
                ('status_anterior', models.CharField(blank=True, editable=False, max_length=20, null=True, verbose_name='Status Anterior')),
                ('tem_ar_condicionado', models.BooleanField(default=True, verbose_name='Ar condicionado')),
                ('tem_tv', models.BooleanField(default=True, verbose_name='TV')),
                ('tem_frigobar', models.BooleanField(default=True, verbose_name='Frigobar')),
                ('tem_wifi', models.BooleanField(default=True, verbose_name='Wi-Fi')),
                ('tem_varanda', models.BooleanField(default=False, verbose_name='Varanda')),
                ('tem_banheira', models.BooleanField(default=False, verbose_name='Banheira')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('data_ultima_manutencao', models.DateField(blank=True, null=True, verbose_name='Última Manutenção')),
                ('data_ultima_limpeza', models.DateField(blank=True, null=True, verbose_name='Última Limpeza')),
                ('area', models.DecimalField(decimal_places=2, help_text='Área em metros quadrados', max_digits=6)),
                ('preco_diaria', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('disponivel', models.BooleanField(default=True)),
                ('desconto_porcentagem', models.IntegerField(default=0, help_text='Desconto em % (0-50%) que pode ser aplicado pelo proprietário', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('proxima_manutencao', models.DateField(blank=True, null=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quartos', to='quartos.categoriaquarto')),
            ],
            options={
                'verbose_name': 'Quarto',
                'verbose_name_plural': 'Quartos',
                'ordering': ['numero'],
            },
        ),
        migrations.AddField(
            model_name='limpezamanutencao',
            name='quarto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarefas', to='quartos.quarto'),
        ),
        migrations.CreateModel(
            name='FotoQuarto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(upload_to='quartos/')),
                ('legenda', models.CharField(blank=True, max_length=100, null=True)),
                ('destaque', models.BooleanField(default=False)),
                ('data_upload', models.DateTimeField(auto_now_add=True)),
                ('quarto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='quartos.quarto')),
            ],
            options={
                'verbose_name': 'Foto do Quarto',
                'verbose_name_plural': 'Fotos dos Quartos',
                'ordering': ['-destaque', 'quarto'],
            },
        ),
    ]
