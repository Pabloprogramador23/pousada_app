# Generated by Django 5.1.7 on 2025-03-24 22:04

import django.db.models.deletion
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
            name='Quarto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10, unique=True)),
                ('andar', models.CharField(choices=[('T', 'Térreo'), ('1', 'Primeiro Andar'), ('2', 'Segundo Andar'), ('3', 'Terceiro Andar')], max_length=1)),
                ('area', models.DecimalField(decimal_places=2, help_text='Área em metros quadrados', max_digits=6)),
                ('preco_diaria', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('disponivel', models.BooleanField(default=True)),
                ('possui_ar_condicionado', models.BooleanField(default=True)),
                ('possui_tv', models.BooleanField(default=True)),
                ('possui_frigobar', models.BooleanField(default=True)),
                ('possui_cofre', models.BooleanField(default=False)),
                ('possui_varanda', models.BooleanField(default=False)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('disponivel', 'Disponível'), ('ocupado', 'Ocupado'), ('manutencao', 'Em Manutenção'), ('limpeza', 'Em Limpeza'), ('reservado', 'Reservado')], default='disponivel', max_length=20)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quartos', to='quartos.categoriaquarto')),
            ],
            options={
                'verbose_name': 'Quarto',
                'verbose_name_plural': 'Quartos',
                'ordering': ['numero'],
            },
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
