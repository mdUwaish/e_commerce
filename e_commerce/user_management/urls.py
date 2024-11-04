from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import Login, PswdUpdate, Profile, ProfileDetail, Register 


urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view()), 
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view()), 
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('profile/', Profile.as_view()),
    path('profile/detail/', ProfileDetail.as_view()),
    path('profile/detail/update/pswd/', PswdUpdate.as_view()),
]