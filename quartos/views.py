from rest_framework import viewsets
from .models import Quarto
from .serializers import QuartoSerializer

class QuartoViewSet(viewsets.ModelViewSet):
    queryset = Quarto.objects.all().order_by('numero')
    serializer_class = QuartoSerializer
