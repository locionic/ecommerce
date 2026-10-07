from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from orders.models import Order, OrderItem
from store.models import Category, Product

User = get_user_model()

MINE_URL = '/api/v1/orders/mine/'
ORDERS_URL = '/api/v1/orders/'


class OrdersApiPermissionsTests(APITestCase):
    """
    Orders expose customer PII, so every non staff user must only ever reach their
    own orders -- through the list route, the detail route and the mine route.
    """

    def setUp(self):
        self.client = APIClient()
        # CustomUser.email is unique and create_user defaults it to '', so pass one per user.
        self.user_a = User.objects.create_user(
            username='alice', email='alice@example.com', password='pass-a-123')
        self.user_b = User.objects.create_user(
            username='bob', email='bob@example.com', password='pass-b-123')

        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)

        category = Category.objects.create(name='Books', created_by=self.user_a)
        self.product = Product.objects.create(
            category=category,
            title='Django for Beginners',
            price='19.99',
            created_by=self.user_a,
        )

        self.order_a = self._create_order(self.user_a, 'cash-aaaaaaaaaaaaaaaa')
        self.order_b = self._create_order(self.user_b, 'cash-bbbbbbbbbbbbbbbb')

    def _create_order(self, user, payment_token):
        order = Order.objects.create(
            first_name=user.username.capitalize(),
            last_name='Tester',
            email=f'{user.username}@example.com',
            address='1 Test Street',
            zipcode=12345,
            place='Testville',
            phone='555-0100',
            paid_amount='19.99',
            payment_token=payment_token,
            cash_on_delivery=True,
            created_by=user,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1,
        )
        return order

    def _authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_anonymous_user_cannot_access_mine(self):
        """The mine route must never serve data to an unauthenticated caller."""
        response = self.client.get(MINE_URL)
        self.assertIn(response.status_code, (401, 403))

    def test_mine_returns_only_own_orders(self):
        """User A's mine listing returns their order and none of user B's PII."""
        self._authenticate(self.token_a)
        response = self.client.get(MINE_URL)

        self.assertEqual(response.status_code, 200)
        tokens = [order['payment_token'] for order in response.data['results']]
        self.assertEqual(tokens, [self.order_a.payment_token])
        self.assertNotIn(self.order_b.payment_token, tokens)

    def test_list_returns_only_own_orders(self):
        """The ordinary list route must be scoped to the requester as well."""
        self._authenticate(self.token_a)
        response = self.client.get(ORDERS_URL)

        self.assertEqual(response.status_code, 200)
        tokens = [order['payment_token'] for order in response.data['results']]
        self.assertEqual(tokens, [self.order_a.payment_token])
        self.assertNotIn(self.order_b.payment_token, tokens)

    def test_cannot_retrieve_other_users_order(self):
        """Retrieving by payment_token must 404 rather than leak the other order."""
        self._authenticate(self.token_a)
        response = self.client.get(f"{ORDERS_URL}{self.order_b.payment_token}/")

        self.assertEqual(response.status_code, 404)

    def test_paginated_response_exposes_expected_keys(self):
        """MyPagination.vue and MyOrdersView.vue both read count/results/next/previous."""
        self._authenticate(self.token_a)
        response = self.client.get(MINE_URL)

        self.assertEqual(response.status_code, 200)
        for key in ('count', 'results', 'next', 'previous'):
            self.assertIn(key, response.data)
        self.assertEqual(response.data['count'], 1)

    def test_superuser_sees_all_orders(self):
        """Staff keep the unfiltered queryset so they can still operate on every order."""
        admin = User.objects.create_superuser(
            username='root', email='root@example.com', password='pass-root-123')
        self._authenticate(Token.objects.create(user=admin))

        response = self.client.get(ORDERS_URL)

        self.assertEqual(response.status_code, 200)
        tokens = {order['payment_token'] for order in response.data['results']}
        self.assertEqual(tokens, {self.order_a.payment_token, self.order_b.payment_token})