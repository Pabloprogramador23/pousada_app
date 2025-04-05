# Generated by Django 5.1.7 on 2025-04-05 12:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('data', models.DateField()),
                ('tipo', models.CharField(choices=[('agua', 'Água'), ('luz', 'Luz'), ('telefone', 'Telefone'), ('pessoal', 'Despesas Pessoais'), ('outros', 'Outros')], max_length=20)),
                ('descricao', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EntradaExtra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('data', models.DateField()),
                ('origem', models.CharField(choices=[('aluguel', 'Aluguel'), ('outros', 'Outros')], max_length=20)),
                ('descricao', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
