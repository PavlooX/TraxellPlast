from rest_framework import serializers
from .models import *


class MaterialSerializer(serializers.ModelSerializer):
    display = serializers.CharField(source='get_name_display')

    class Meta:
        model = Material
        fields = ['name', 'display', 'price']        


class ColorSerializer(serializers.ModelSerializer):
    display = serializers.CharField(source='get_name_display')

    class Meta:
        model = Color
        fields = ['name', 'display']


class ProductSerializer(serializers.ModelSerializer):    
    model = serializers.FileField(use_url=False)
    model_url = serializers.SerializerMethodField()
    materials = MaterialSerializer(many=True)
    colors = ColorSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'model', 'model_url', 'name', 'amount_min', 'materials', 'colors']
        
    def get_model_url(self, obj):
        return obj.model_url


class ItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    material = MaterialSerializer()
    color = ColorSerializer()

    class Meta:
        model = Item
        fields = ['id', 'product', 'material', 'color', 'custom_color', 'amount']


class OrderSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Order
        fields = ['id', 'order_status', 'in_process_date', 'shipped_date']