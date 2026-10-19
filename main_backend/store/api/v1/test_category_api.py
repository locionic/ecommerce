import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from store.models import Product, Category


class CategoryApiTestCase(TestCase):
    """
    A test case class to test Categories API.
    Test cases:
        test_category_list()
        test_category_retrieve()
        test_category_retrieve_filters_inactive_products()
        test_category_retrieve_filters_out_of_stock_products()
        test_category_pagination()
        test_category_create_by_admin()
        test_category_create_by_non_admin()
        test_category_create_unauthenticated()
    """
    
    def setUp(self):
        """
        Initial setup with admin, seller, and customer users,
        categories, and products.
        """
        self.UserModel = get_user_model()
        
        self.admin = self.UserModel.objects.create_user(
            email="testadmin@example.com", username='admin', password="password3",
            is_staff=True, is_superuser=True
        )
        self.seller = self.UserModel.objects.create_user(
            email="test@example.com", username='seller', password="password", is_seller=True
        )
        self.user = self.UserModel.objects.create_user(
            email="test2@example.com", username='user', password="password2"
        )
        
        # Create categories
        self.category_clothes = Category.objects.create(
            name='Clothes',
            slug='clothes',
            created_at=timezone.now(),
            created_by=self.admin
        )
        self.category_laptops = Category.objects.create(
            name='Laptops',
            slug='laptops',
            created_at=timezone.now(),
            created_by=self.admin
        )
        self.category_phones = Category.objects.create(
            name='Phones',
            slug='phones',
            created_at=timezone.now(),
            created_by=self.admin
        )
        
        # Create products for Clothes category (some inactive/out of stock)
        Product.objects.create(
            category=self.category_clothes,
            title="T-shirt Active In Stock",
            slug='t-shirt-active-instock',
            description='Green T-shirt',
            price=125.25,
            created_by=self.seller,
            in_stock=True,
            is_active=True,
            created_at=timezone.now()
        )
        Product.objects.create(
            category=self.category_clothes,
            title="T-shirt Inactive In Stock",
            slug='t-shirt-inactive-instock',
            description='Blue T-shirt',
            price=100.00,
            created_by=self.seller,
            in_stock=True,
            is_active=False,  # Inactive
            created_at=timezone.now()
        )
        Product.objects.create(
            category=self.category_clothes,
            title="T-shirt Active Out of Stock",
            slug='t-shirt-active-outofstock',
            description='Red T-shirt',
            price=75.50,
            created_by=self.seller,
            in_stock=False,  # Out of stock
            is_active=True,
            created_at=timezone.now()
        )
        Product.objects.create(
            category=self.category_clothes,
            title="T-shirt Inactive Out of Stock",
            slug='t-shirt-inactive-outofstock',
            description='Yellow T-shirt',
            price=50.00,
            created_by=self.seller,
            in_stock=False,
            is_active=False,
            created_at=timezone.now()
        )
        
        # Create products for Laptops category (all active and in stock)
        Product.objects.create(
            category=self.category_laptops,
            title="Asus TUF F-15",
            slug='asus_tuf_f-15',
            description='8GB RAM 15.6" FHD display',
            price=12000.00,
            created_by=self.admin,
            in_stock=True,
            is_active=True,
            created_at=timezone.now()
        )
        Product.objects.create(
            category=self.category_laptops,
            title="MacBook Pro",
            slug='macbook_pro',
            description='M2 chip 16GB RAM',
            price=25000.00,
            created_by=self.admin,
            in_stock=True,
            is_active=True,
            created_at=timezone.now()
        )
        
        # Create products for Phones category (all active and in stock)
        Product.objects.create(
            category=self.category_phones,
            title="iPhone 15",
            slug='iphone_15',
            description='Latest iPhone',
            price=15000.00,
            created_by=self.admin,
            in_stock=True,
            is_active=True,
            created_at=timezone.now()
        )
        
        # Override test client
        self.client = APIClient()
        self.admin_token = Token.objects.create(user=self.admin)
        self.seller_token = Token.objects.create(user=self.seller)
        self.user_token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)

    def test_category_list(self):
        """
        Test the category list API returns all categories.
        """
        resp = self.client.get("/api/v1/categories/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        data = resp.json()
        
        # Paginated response
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 3)
        
        # Check ordering by name (from model Meta)
        self.assertEqual(data['results'][0]['name'], 'Clothes')
        self.assertEqual(data['results'][1]['name'], 'Laptops')
        self.assertEqual(data['results'][2]['name'], 'Phones')

    def test_category_retrieve(self):
        """
        Test retrieving a category returns the category with filtered products
        (only active and in_stock).
        """
        resp = self.client.get("/api/v1/categories/clothes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Check response structure
        self.assertIn('category', data)
        self.assertIn('products', data)
        
        # Check category data
        self.assertEqual(data['category']['name'], 'Clothes')
        self.assertEqual(data['category']['slug'], 'clothes')
        
        # Check products - only 1 should be returned (active AND in_stock)
        # We created 4 products, only 1 is both active and in_stock
        self.assertEqual(data['products']['count'], 1)
        self.assertEqual(len(data['products']['results']), 1)
        self.assertEqual(data['products']['results'][0]['title'], 'T-shirt Active In Stock')
        self.assertEqual(data['products']['results'][0]['in_stock'], True)
        self.assertEqual(data['products']['results'][0]['is_active'], True)

    def test_category_retrieve_filters_inactive_products(self):
        """
        Test that inactive products are filtered out in category retrieve.
        """
        resp = self.client.get("/api/v1/categories/clothes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Only 1 product should be returned (the one that is active AND in_stock)
        product_titles = [p['title'] for p in data['products']['results']]
        self.assertNotIn('T-shirt Inactive In Stock', product_titles)
        self.assertNotIn('T-shirt Inactive Out of Stock', product_titles)

    def test_category_retrieve_filters_out_of_stock_products(self):
        """
        Test that out of stock products are filtered out in category retrieve.
        """
        resp = self.client.get("/api/v1/categories/clothes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Only 1 product should be returned
        product_titles = [p['title'] for p in data['products']['results']]
        self.assertNotIn('T-shirt Active Out of Stock', product_titles)
        self.assertNotIn('T-shirt Inactive Out of Stock', product_titles)

    def test_category_pagination(self):
        """
        Test category pagination works correctly.
        """
        # Laptops has 2 products, page size is 20 by default
        resp = self.client.get("/api/v1/categories/laptops/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data['products']['count'], 2)
        self.assertEqual(len(data['products']['results']), 2)
        self.assertIsNone(data['products']['next'])
        self.assertIsNone(data['products']['previous'])

    def test_category_create_by_admin(self):
        """
        Test that admin can create a category.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        category_dict = {
            "name": "Accessories",
            "slug": "accessories",
        }
        resp = self.client.post("/api/v1/categories/", category_dict)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Category.objects.count(), 4)
        
        # Verify the created category
        created_category = Category.objects.get(slug='accessories')
        self.assertEqual(created_category.name, 'Accessories')
        self.assertEqual(created_category.created_by, self.admin)

    def test_category_create_by_non_admin(self):
        """
        Test that non-admin (seller) cannot create a category.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        category_dict = {
            "name": "Accessories",
            "slug": "accessories",
        }
        resp = self.client.post("/api/v1/categories/", category_dict)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Category.objects.count(), 3)

    def test_category_create_unauthenticated(self):
        """
        Test that unauthenticated user cannot create a category.
        """
        self.client.credentials()
        category_dict = {
            "name": "Accessories",
            "slug": "accessories",
        }
        resp = self.client.post("/api/v1/categories/", category_dict)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(Category.objects.count(), 3)

    def test_category_retrieve_empty_category(self):
        """
        Test retrieving a category with no active/in_stock products.
        """
        # Create a category with no products
        empty_category = Category.objects.create(
            name='Empty Category',
            slug='empty-category',
            created_by=self.admin
        )
        
        resp = self.client.get("/api/v1/categories/empty-category/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data['category']['name'], 'Empty Category')
        self.assertEqual(data['products']['count'], 0)
        self.assertEqual(len(data['products']['results']), 0)
        self.assertIsNone(data['products']['next'])
        self.assertIsNone(data['products']['previous'])

    def test_category_retrieve_nonexistent(self):
        """
        Test retrieving a non-existent category returns 404.
        """
        resp = self.client.get("/api/v1/categories/nonexistent/")
        self.assertEqual(resp.status_code, 404)

    def test_category_update_by_admin(self):
        """
        Test that admin can update a category.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        updated_data = {
            "name": "Updated Clothes",
            "slug": "clothes",
        }
        resp = self.client.put("/api/v1/categories/clothes/", updated_data)
        self.assertEqual(resp.status_code, 200)
        
        updated_category = Category.objects.get(slug='clothes')
        self.assertEqual(updated_category.name, 'Updated Clothes')

    def test_category_update_by_non_admin(self):
        """
        Test that non-admin cannot update a category.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        updated_data = {
            "name": "Updated Clothes",
            "slug": "clothes",
        }
        resp = self.client.put("/api/v1/categories/clothes/", updated_data)
        self.assertEqual(resp.status_code, 403)

    def test_category_delete_by_admin(self):
        """
        Test that admin can delete a category.
        """
        # Create an empty category without products to test deletion
        empty_category = Category.objects.create(
            name='Category to Delete',
            slug='category-to-delete',
            created_by=self.admin
        )
        
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        resp = self.client.delete("/api/v1/categories/category-to-delete/")
        self.assertEqual(resp.status_code, 204)
        # Count should go from 3 (initial) + 1 (new) - 1 (deleted) = 3
        self.assertEqual(Category.objects.count(), 3)

    def test_category_delete_by_non_admin(self):
        """
        Test that non-admin cannot delete a category.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        resp = self.client.delete("/api/v1/categories/phones/")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Category.objects.count(), 3)

    def test_category_retrieve_uses_select_related(self):
        """
        Test that category retrieve properly filters products using the optimized queryset.
        """
        # Laptops category has 2 active/in_stock products
        resp = self.client.get("/api/v1/categories/laptops/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data['products']['count'], 2)
        product_titles = [p['title'] for p in data['products']['results']]
        self.assertIn('Asus TUF F-15', product_titles)
        self.assertIn('MacBook Pro', product_titles)
        
        # Verify all returned products are active and in_stock
        for product in data['products']['results']:
            self.assertTrue(product['is_active'])
            self.assertTrue(product['in_stock'])

    def test_search_not_applied_to_category_retrieve(self):
        """
        Test that search parameter does not apply to category retrieve
        (category retrieve has its own filtering logic).
        """
        # Try searching within a category - this should not filter the products
        # since the category retrieve endpoint doesn't use the search parameter
        resp = self.client.get("/api/v1/categories/clothes/?search=tshirt")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Should still return only 1 product (the active in_stock one)
        # not apply the search filter to the category's products
        self.assertEqual(data['products']['count'], 1)
