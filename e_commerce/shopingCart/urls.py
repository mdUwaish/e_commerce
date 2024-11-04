from django.urls import path
from .views import OrderHistory, addCart, removeCart, detailCart, addressDetail, addressList, PaymentAPI, updateCart, Checkout, OrderSummary
from .views import OrderTracking, SellerDashboard, AdminAnalyticsDashboard, sendMail, NotificationListView

urlpatterns = [
    path('product/add/', addCart.as_view()),
    path('product/remove/', removeCart.as_view()),
    path('product/detail/', detailCart.as_view()),
    path('address/all/', addressList.as_view()),
    path('address/create/', addressList.as_view()),
    path('address/view/', addressDetail.as_view()),
    path('address/update/', addressDetail.as_view()),
    path('address/delete/', addressDetail.as_view()),
    path('payment/', PaymentAPI.as_view()),
    path('product/update/', updateCart.as_view()),
    path('checkout/', Checkout.as_view(),),
    path('order/summary/<int:order_id>/', OrderSummary.as_view()),
    path('order/history/', OrderHistory.as_view()),
    path('order/track/', OrderTracking.as_view()),
    path('order/status/<int:order_id>', SellerDashboard.as_view()),
    path('seller/dashboard/', SellerDashboard.as_view()),
    path('admin/analytics/', AdminAnalyticsDashboard.as_view()),
    path('mail/', sendMail.as_view()),
    path('notification/', NotificationListView.as_view())
]
