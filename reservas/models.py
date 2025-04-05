from django.db import models
from hospedes.models import Hospede
from quartos.models import Quarto
from .services import calcular_valor_reserva

class Reserva(models.Model):
    cliente = models.ForeignKey(Hospede, on_delete=models.CASCADE)
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE)
    data_checkin = models.DateField()
    data_checkout = models.DateField()
    numero_pessoas = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    pago_50 = models.BooleanField(default=False)
    confirmado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.valor_total = calcular_valor_reserva(self)
        super().save(*args, **kwargs)
