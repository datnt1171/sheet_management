from rest_framework import serializers
from myapp.models import Table  # Assuming you have a Table model

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'name', 'data']
