from rest_framework import serializers
from .models import User
from .manage import UserManager

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(style= {'input_type':'password'}, write_only=True)
    class Meta:
        model= User
        fields= ['first_name', 'last_name','email','password','role', 'phone_number','confirm_password']
    
    def create(self, validated_data):
        del validated_data['confirm_password']
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['first_name','last_name','email','password','role', 'phone_number']
