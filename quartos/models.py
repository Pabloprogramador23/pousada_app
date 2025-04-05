from django.db import models

class Quarto(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    tem_ventilador = models.BooleanField(default=True)

    def __str__(self):
        return f"Quarto {self.numero} - {'Ventilador' if self.tem_ventilador else 'Normal'}"
