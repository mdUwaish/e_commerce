from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user_management.urls')),
    path('product/', include('product_management.urls')),
    path('cart/', include(('shopingCart.urls', 'cart'), namespace='cart')),
]
