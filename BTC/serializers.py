from rest_framework import serializers
from BTC.models import PriceAlert


class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = '__all__'
