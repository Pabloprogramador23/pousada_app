from .models import Reserva
from .services import existe_conflito_de_reserva
from .serializers import ReservaSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        quarto_id = data.get('quarto')
        checkin = data.get('data_checkin')
        checkout = data.get('data_checkout')

        if existe_conflito_de_reserva(quarto_id, checkin, checkout, Reserva):
            return Response(
                {"erro": "O quarto já está reservado nesse período."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)
