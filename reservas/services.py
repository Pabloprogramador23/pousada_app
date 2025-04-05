from django.db.models import Q

def calcular_valor_reserva(reserva):
    dias = (reserva.data_checkout - reserva.data_checkin).days
    if reserva.quarto.tem_ventilador:
        preco = 70 if reserva.numero_pessoas > 1 else 140
    else:
        preco = 80 if reserva.numero_pessoas > 1 else 160
    return preco * dias

def existe_conflito_de_reserva(quarto_id, checkin, checkout, reserva_model_class):
    return reserva_model_class.objects.filter(
        quarto_id=quarto_id,
        confirmado=True
    ).filter(
        Q(data_checkin__lt=checkout) & Q(data_checkout__gt=checkin)
    ).exists()
