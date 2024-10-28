from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, RegisterSerializer 
from .models import User
from .utils import get_tokens_for_user

# Create your views here.
class Register(APIView):
    def post(self, request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email and not password:
            return Response({'message':'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        token= get_tokens_for_user(user)
        return Response({'message':'Login successful','token':token}, status=status.HTTP_200_OK)
        


class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PswdUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        curr_password = request.data.get('curr_password')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password != confirm_password:
            return Response({'message':'Password and Confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user

        if user.check_password(curr_password):
            user.set_password(password)
            user.save()
            return Response({'message':'Password Changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message':'current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

