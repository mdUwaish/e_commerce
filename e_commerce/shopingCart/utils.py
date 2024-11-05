from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(user_email, order_id):
    subject = 'Order Confirmation'
    message = f'Thank you for your order! Your order ID is {order_id}.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])

def send_shipping_update_email(user_email, order_status):
    subject = 'Shipping Update'
    message = f'Your order status has been updated to {order_status}.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
