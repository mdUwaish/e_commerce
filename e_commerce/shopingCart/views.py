from django.http import Http404
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from product_management.models import Product
from .models import Cart, Address, Order, OrderItem, Notification
from .serializers import AddressSerializer, CardInformationSerializer, OrderSerializer, OrderItemSerializer, NotificationSerializer
import stripe
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_order_confirmation_email



class addCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
            message=  "Item added to your cart"
        else:
            Cart.objects.create(user=request.user, product=product)
            message = "Item added to your cart"

        return Response({"message":message})


class removeCart(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        item_id = request.data.get('item_id')
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.delete()
        return Response({"message": "Item removed from your cart"})
    

class detailCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.quantity * item.product.price for item in cart_items)

        cart_data = {
            "items": [{"product": item.product.name, "quantity": item.quantity, "price": item.product.price} for item in cart_items],
            "total_price": total_price,
        }

        return Response({"message": "Cart items retrieved", "cart": cart_data})


class addressList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        snippets =Address.objects.filter(user=user)
        serializer = AddressSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class addressDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Address.objects.get(pk=pk)
        except Address.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        pk = request.data.get('id')
        snippet = self.get_object(pk)
        serializer = AddressSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, format=None):
        pk = request.data.get('id')
        snippet = self.get_object(pk)
        serializer = AddressSerializer(snippet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        pk = request.data.get('id')
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentAPI(APIView):
    serializer_class = CardInformationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            stripe.api_key = 'STRIPE_SECRET_KEY'
            response = self.stripe_card_payment(data_dict=data_dict)
        else:
            response = {
                'errors': serializer.errors,
                'status': status.HTTP_400_BAD_REQUEST
            }
        return Response(response)

    def stripe_card_payment(self, data_dict):
        try:
            card_details = {
                "type": "card",
                "card": {
                    "number": data_dict['card_number'],
                    "exp_month": data_dict['expiry_month'],
                    "exp_year": data_dict['expiry_year'],
                    "cvc": data_dict['cvc'],
                },
            }
            payment_intent = stripe.PaymentIntent.create(
                amount=10000, 
                currency='inr',
            )
            payment_intent_modified = stripe.PaymentIntent.modify(
                payment_intent['id'],
                payment_method=card_details['id'],
            )
            try:
                payment_confirm = stripe.PaymentIntent.confirm(
                    payment_intent['id']
                )
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
            except:
                payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
                payment_confirm = {
                    "stripe_payment_error": "Failed",
                    "code": payment_intent_modified['last_payment_error']['code'],
                    "message": payment_intent_modified['last_payment_error']['message'],
                    'status': "Failed"
                }
            if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
                response = {
                    'message': "Card Payment Success",
                    'status': status.HTTP_200_OK,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm
                }
            else:
                response = {
                    'message': "Card Payment Failed",
                    'status': status.HTTP_400_BAD_REQUEST,
                    "card_details": card_details,
                    "payment_intent": payment_intent_modified,
                    "payment_confirm": payment_confirm
                }
        except:
            response = {
                'error': "Your card number is incorrect",
                'status': status.HTTP_400_BAD_REQUEST,
                "payment_intent": {"id": "Null"},
                "payment_confirm": {'status': "Failed"}
            }
        return response


class updateCart(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        if quantity < 1:
            return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()
        return Response({"message": "Cart updated successfully"})


class Checkout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        address_id = request.data.get('address_id')
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(Address, id=address_id, user=request.user)
        total_price = sum(item.quantity * item.product.price for item in cart_items)

        order = Order.objects.create(user=request.user, address=address, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
            )
        cart_items.delete()
        send_order_confirmation_email(request.user.email, order.id)
        return Response({"message": "Order created successfully", "order_id": order.id})


class OrderSummary(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response({"message": "Order history retrieved successfully", "orders": serializer.data})


class OrderTracking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response({"message": "Order status retrieved successfully", "order": serializer.data})


class SellerDashboard(APIView):
    permission_classes= [IsAuthenticated]

    def get(self, request):
        if not request.user:
            return Response({"message":"Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        orders=Order.objects.filter(user_id=request.user).distinct()
        serializer=OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def put(self, request, order_id):
        if not request.user:
            return Response({"message":"Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        order = get_object_or_404(Order, id=order_id, user_id=request.user)
        status=request.data.get('status')
        if status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response({"message":"Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status=status
        order.save()
        return Response({"message":"Status updated sucessfully", "order_id":order_id, "status":order.status})
    

class  AdminAnalyticsDashboard(APIView):
    permission_classes= [IsAuthenticated]

    def get_sales_analytics(self):
        total_sale= Order.objects.filter(status="Delivered").count()
        total_revenue= Order.objects.filter(status="Delivered").aggregate(Sum('total_price'))['total_price__sum']

        last_month = datetime.now() - timedelta(days=30)
        last_month_sales = Order.objects.filter(status="Delivered", created_at__gte=last_month).count()
        growth_rate = ((last_month_sales / total_sale) * 100) if total_sale else 0
        
        return {
            "total_sales": total_sale,
            "total_revenue": total_revenue,
            "growth_rate": growth_rate
        }
    
    def get_user_behavior_analytics(self):
        most_viewed_products = Product.objects.all().order_by('-id')[:5]
        abandoned_carts = Cart.objects.filter(quantity__gt=0).count()
        conversion_rate = (Order.objects.count() / Cart.objects.count()) * 100 if Cart.objects.count() else 0

        return {
            "most_viewed_products": [product.name for product in most_viewed_products],
            "abandoned_carts": abandoned_carts,
            "conversion_rate": conversion_rate
        }
    
    def get_inventory_management(self):
        low_stock_products = Product.objects.filter(stock__lt=10)
        return {
            "low_stock_products": [
                {"name": product.name, "stock": product.stock} for product in low_stock_products
            ]
        }

    def get_custom_reports(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date and end_date:
            orders = Order.objects.filter(created_at__range=[start_date, end_date])
            report_data = {
                "total_sales": orders.count(),
                "total_revenue": orders.aggregate(Sum('total_price'))['total_price__sum']
            }
        else:
            report_data = {"error": "Please provide a valid start and end date."}
        
        return report_data

    def get(self, request):
        response_data = {
            "sales_analytics": self.get_sales_analytics(),
            "user_behavior_analytics": self.get_user_behavior_analytics(),
            "inventory_management": self.get_inventory_management(),
        }
        
        custom_report = self.get_custom_reports(request)
        if custom_report:
            response_data["custom_reports"] = custom_report
            
        return Response(response_data, status=status.HTTP_200_OK)


class sendMail(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        address = request.data.get('address')
        subject = request.data.get('subject')
        message = request.data.get('message')

        context= {}
        if address and subject and message:
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                context['result'] = 'Email sent successfully'
            except Exception as e:
                context['result'] = f'Error sending email: {e}'
        else:
            context['result'] = 'All fields are required'
    
        return Response(context)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        notification_id = request.data.get('notification_id')
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"})