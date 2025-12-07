from rest_framework import serializers
from .models import Library

class LibrarySerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Library
        fields = ['id', 'name', 'street', 'postcode', 'opening_hours', 'phone', 'website', 'operator', 'wheelchair', 'coordinates']

    def get_coordinates(self, obj):
        if obj.geom:
            return [obj.geom.x, obj.geom.y]  # longitude, latitude
        return None
