from rest_framework import serializers
from .models import Quarto

class QuartoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quarto
        fields = '__all__'

