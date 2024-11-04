from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import ProductCreate, ProductDetail, ReviewListCreate, ProductList

urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', ProductList.as_view(), name='product-list'),
    path('create/', ProductCreate.as_view(), name='product-create'),
    path('<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('<int:pk>/reviews/', ReviewListCreate.as_view(), name='review-list-create'),
    # path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
]
