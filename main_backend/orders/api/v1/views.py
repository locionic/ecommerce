import random
import string

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache, cache_control
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework import viewsets, status, authentication, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from src.paypal.django_client import get_paypal_client
from orders.models import Order
from orders.api.v1.serializers import OrderSerializer, MyOrderSerializer
from django.utils.decorators import method_decorator

# @method_decorator(never_cache, name='get_queryset')
# @never_cache
class OrderViewSet(viewsets.ModelViewSet):
    """
    TODO:set more permissions to allow only super user to see the all orders and payers to see their customers' orders
    """
    lookup_field = "payment_token"
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = OrderSerializer

    # @method_decorator(cache_page(5))
    # def get_queryset(self, request):
    #     # self.queryset = Order.objects.all()
    #     # return self.queryset
    #     # queryset = super(OrderViewSet, self).get_queryset()
    #     queryset = self.queryset.all()
    #     print('queryset here: ', queryset)
    #     return queryset

    # def list(self, request, *args, **kwargs):
    #     print('override or not?')
    #     serializer = self.serializer_class(self.queryset.all(), many=True)
    #     return Response(serializer.data)

    # def list(self, request):
    #     pass

    # def create(self, request):
    #     pass

    # def retrieve(self, request, pk=None):
    #     pass

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass

    # def list(self, request, *args, **kwargs):
    #     print('fuck?')

    # @method_decorator(never_cache)
    # def list(self, request, *args, **kwargs):
    #     queryset.all()
    #     return super().list(request, *args, *kwargs)

    def get_serializer_class(self):
        if self.action == "mine":
            print('specify what is serializer class: ', self.action)
            return MyOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        print('vao ay achua???')
        serializer = self.serializer_class(data=request.data)
        print(serializer.is_valid())
        print('khong valid a?')
        if serializer.is_valid():
            print('tai sao 01')
            paid_amount = sum(
                item.get('quantity') * item.get('product').price for item in serializer.validated_data['items']
            )
            print('tai sao 02')
            cash_on_delivery = serializer.validated_data["cash_on_delivery"]
            print('tai sao 03')

            if cash_on_delivery:
                generated_key = 'cash-' + ''.join(random.choice(string.ascii_lowercase) for _ in range(16))
                serializer.save(created_by=request.user, paid_amount=paid_amount, payment_token=generated_key)
                print('tai sao 05')
                self.queryset = self.queryset.all()
                print(self.queryset)
                print('tong cong bao nhieu')
                print(self.queryset.count())
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print('tai sao 04')
            order = get_paypal_client().create_order(paid_amount,
                                                     return_url=request.data.get('return_url', "http://localhost:8080"),
                                                     cancel_url=request.data.get('cancel_url', "http://localhost:8080")
                                                     )
            print('tai sao 07')                                                        
            serializer.save(created_by=request.user, paid_amount=paid_amount, payment_token=order.get('id'))
            # self.queryset = self.queryset.all()
            print('create roi?')
            print(order)
            print('ahahhahhah')
            self.queryset = self.queryset.all()
            print(self.queryset)
            print('tong cong bao nhieu')
            print(self.queryset.count())
            return Response(
                {
                    "paypal": [
                        order
                    ],
                    "results": [
                        serializer.data
                    ]
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, name="Capture the payment")
    def capture(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Images are yours")
        payment_token = request.data.get('token', None)
        if payment_token:
            order = get_paypal_client().capture_payment(payment_token)
            order_status = order.get('status', None)
            if order_status == 'COMPLETED':
                order = Order.objects.get(payment_token=payment_token)
                order.paid = True
                order.save()
                return Response({"status": "COMPLETED"}, status=status.HTTP_201_CREATED)
            elif order.get('details')[0].get('issue') == 'ORDER_ALREADY_CAPTURED':
                return Response({"status": "ORDER_ALREADY_CAPTURED"}, status=status.HTTP_201_CREATED)
            elif order.get('details')[0].get('issue') == 'ORDER_NOT_APPROVED':
                return Response({"status": "ORDER_NOT_APPROVED"}, status=status.HTTP_201_CREATED)
            elif order.get('details')[0].get('issue') == 'INVALID_RESOURCE_ID':
                return Response({"status": "INVALID_RESOURCE_ID"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"token": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "unknown error has been happened"}, status=status.HTTP_400_BAD_REQUEST)
