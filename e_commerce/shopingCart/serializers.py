from rest_framework import serializers
from .models import Address, Order, OrderItem, Notification
import datetime

def check_expiry_month(value):
    if not 1 <= int(value) <= 12:
        raise serializers.ValidationError("Invalid expiry month.")

def check_expiry_year(value):
    today = datetime.datetime.now()
    if not int(value) >= today.year:
        raise serializers.ValidationError("Invalid expiry year.")

def check_cvc(value):
    if not 3 <= len(value) <= 4:
        raise serializers.ValidationError("Invalid CVC number.")

def check_payment_method(value):
    payment_method = value.lower()
    if payment_method not in ["card"]:
        raise serializers.ValidationError("Invalid payment method.")

class CardInformationSerializer(serializers.Serializer):
    card_number = serializers.CharField(
        max_length=150,
        required=True
    )
    expiry_month = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_month]
    )
    expiry_year = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_expiry_year]
    )
    cvc = serializers.CharField(
        max_length=150,
        required=True,
        validators=[check_cvc]
    )


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user','line', 'city','state','country','pin_code']
        extra_kwargs = {'user': {'read_only': True}}


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['user', 'address', 'total_price', 'created_at', 'status', 'items']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model:Notification
        fields= ['id','message','is_read','created_at']