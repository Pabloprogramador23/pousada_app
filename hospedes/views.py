from rest_framework import viewsets
from .models import Hospede
from .serializers import HospedeSerializer

class HospedeViewSet(viewsets.ModelViewSet):
    queryset = Hospede.objects.all().order_by('-data_cadastro')
    serializer_class = HospedeSerializer
