import json
from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from pytz import UTC
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from store.models import Product, Category, Review


class ProductApiTestCase(TestCase):
    """
    A test case class to test Products API.
    Test cases:
        test_product_list()
        test_unauthenticated_product_create()
        test_customer_product_create()
        test_seller_product_create()
        test_post_create()
        test_product_update_by_owner()
        test_product_update_by_admin()
        test_product_update_by_unauthenticated_user()
        test_create_review_for_product_by_authenticated_user()
        test_create_review_for_product_by_unauthenticated_user()
    """
    def setUp(self):
        """
        Initial setup with 3 users (admin, seller, customer), 2 Categories, 2 Products, and API Client.
        """
        self.seller = get_user_model().objects.create_user(
            email="test@example.com", username='seller', password="password", is_seller=True
        )
        self.admin = get_user_model().objects.create_user(
            email="testadmin@example.com", username='admin', password="password3", is_staff=True, is_superuser=True
        )

        self.user = get_user_model().objects.create_user(
            email="test2@example.com", username='user', password="password2"
        )
        categories = [
            Category.objects.create(
                name='Clothes',
                slug='clothes',
                created_at=timezone.now(),
                created_by=self.admin
            ),
            Category.objects.create(
                name='Laptops',
                slug='laptops',
                created_at=timezone.now(),
                created_by=self.admin
            ),
        ]
        products = [
            Product.objects.create(
                category=categories[0],
                title="T-shirt",
                slug='t-shirt',
                description='Green T-shirt',
                price=125.25,
                created_by=self.seller,
                in_stock=True,
                is_active=True,
                created_at=timezone.now()
            ),
            Product.objects.create(
                category=categories[1],
                title="Asus TUF F-15",
                slug='asus_tuf_f-15',
                description='8GB RAM 15.6" FHD display',
                price=12000.00,
                created_by=self.admin,
                in_stock=True,
                is_active=True,
                created_at=timezone.now()
            ),
        ]

        # let us look up the post info by slug
        self.product_lookup = {p.slug: p for p in products}

        # override test client
        self.client = APIClient()
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.seller_token = Token.objects.create(user=self.seller)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)

    def create_product_and_review_for_test(self):
        """
        Non-test method that create a product and review instance for tests
        """
        product = Product.objects.create(
            category_id=1,
            title="Asus TUF F-15",
            slug='laptop_asus',
            description='8GB RAM 15.6" FHD display',
            price=2000.00,
            created_by=self.seller,
            created_at=timezone.now()
        )
        resp = self.client.get(f"/api/v1/products/{product.slug}/")
        self.assertEqual(resp.status_code, 200)
        review = {
            "rate": 10,
            "content": "Good product"
        }

        product_patch = {
            "reviews": [
                review
            ]
        }
        return {"product_patch": product_patch, "product": product, "review": review}

    def test_product_list(self):
        """
        Test the product api link with GET request to check if it returns a list or products as a json response.
        Check if the products return are the products in the setUp().
        """
        resp = self.client.get("/api/v1/products/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        data = resp.json()["results"]
        self.assertEqual(len(data), 2)

        for product_dict in data:
            product_obj = self.product_lookup[product_dict["slug"]]
            self.assertEqual(product_obj.title, product_dict["title"])
            self.assertEqual(product_obj.slug, product_dict["slug"])
            self.assertEqual(product_obj.description, product_dict["description"])
            self.assertEqual(product_obj.price, float(product_dict["price"]))
            self.assertEqual(product_obj.in_stock, product_dict["in_stock"])
            self.assertEqual(product_obj.is_active, product_dict["is_active"])
            self.assertTrue(
                product_dict["created_by"].endswith(f"/api/v1/users/{product_obj.created_by.username}")
            )
            self.assertEqual(
                product_obj.created_at,
                datetime.strptime(
                    product_dict["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ).replace(tzinfo=UTC),
            )

    def test_unauthenticated_product_create(self):
        """
        Check if the unauthenticated user can create a product
        """
        # unset credentials so we are an anonymous user
        self.client.credentials()
        product_dict = {
            "category": 1,
            "title": "Asus TUF F-155",
            "slug": 'asus_tuf_f-155',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
            "in_stock": True,
            "is_active": True,
            "created_at": timezone.now()
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(Product.objects.all().count(), 2)

    def test_customer_product_create(self):
        """
        Check if a normal user can create a product
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
        product_dict = {
            "category": 1,
            "title": "Asus TUF F-155",
            "slug": 'asus_tuf_f-155',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
            "in_stock": True,
            "is_active": True,
            "created_at": timezone.now()
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Product.objects.all().count(), 2)

    def test_seller_product_create(self):
        """
        Check if a seller user can create a product
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        product_dict = {
            "category": 1,
            "title": "Asus TUF F-515",
            "slug": 'asus_tuf_f-155',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
            "in_stock": True,
            "is_active": True,
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.all().count(), 3)

    def test_post_create(self):
        """
        Check if the post created as excepted with POST request.
        Superuser credentials used.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        product_dict = {
            "category": 1,
            "title": "Asus TUF F-515",
            "slug": 'asus_tuf_f33-155',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
            "in_stock": True,
            "is_active": True,
            "created_at": timezone.now()
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        product_slug = resp.json()["slug"]
        product_obj = Product.objects.get(slug=product_slug)

        self.assertEqual(product_obj.title, product_dict["title"])
        self.assertEqual(product_obj.slug, product_dict["slug"])
        self.assertEqual(product_obj.description, product_dict["description"])
        self.assertEqual(product_obj.price, float(product_dict["price"]))
        self.assertEqual(product_obj.in_stock, product_dict["in_stock"])
        self.assertEqual(product_obj.is_active, product_dict["is_active"])
        self.assertEqual(product_obj.created_by, self.admin)

    def test_product_update_by_owner(self):
        """
            Test editing the product by the seller who created it using PATCH and PUT requests.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        # create a new product
        product_dict = {
            "category": 1,
            "title": "Asus TUF",
            "slug": 'asus_tuf',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.all().count(), 3)
        product_slug = resp.json()["slug"]
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.in_stock, False)
        self.assertEqual(product_obj.is_active, False)

        # Update the product with PATCH request
        product_patch = {"in_stock": True, "is_active": True}
        resp = self.client.patch(f"/api/v1/products/{product_slug}/", product_patch)
        self.assertEqual(resp.status_code, 200)
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.in_stock, True)
        self.assertEqual(product_obj.is_active, True)

        # Update the product with PUT request
        resp = self.client.get(f"/api/v1/products/{product_slug}/")
        product_dict = resp.json()
        product_dict['price'] = 5000
        product_dict['title'] = "Asus Tuf A15"
        product_dict['thumbnail'] = ""
        resp = self.client.put(f"/api/v1/products/{product_slug}/", product_dict)
        self.assertEqual(resp.status_code, 200)
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.title, product_dict["title"])
        self.assertEqual(product_obj.price, float(product_dict["price"]))
        self.assertEqual(product_obj.is_active, product_dict["is_active"])
        self.assertEqual(product_obj.created_by, self.seller)

    def test_product_update_by_admin(self):
        """
            Test editing the product by the staff user using PATCH and PUT requests.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        # create a new product
        product_dict = {
            "category": 1,
            "title": "Asus TUF",
            "slug": 'asus_tuf',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.all().count(), 3)
        product_slug = resp.json()["slug"]
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.in_stock, False)
        self.assertEqual(product_obj.is_active, False)

        # Update the product with PATCH request
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        product_patch = {"in_stock": True, "is_active": True}
        resp = self.client.patch(f"/api/v1/products/{product_slug}/", product_patch)
        self.assertEqual(resp.status_code, 200)
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.in_stock, True)
        self.assertEqual(product_obj.is_active, True)

        # Update the product with PUT request
        resp = self.client.get(f"/api/v1/products/{product_slug}/")
        product_dict = resp.json()
        product_dict['price'] = 5000
        product_dict['title'] = "Asus Tuf A15"
        product_dict['thumbnail'] = ""
        resp = self.client.put(f"/api/v1/products/{product_slug}/", product_dict)
        self.assertEqual(resp.status_code, 200)
        product_obj = Product.objects.get(slug=product_slug)
        self.assertEqual(product_obj.title, product_dict["title"])
        self.assertEqual(product_obj.price, float(product_dict["price"]))
        self.assertEqual(product_obj.is_active, product_dict["is_active"])
        self.assertEqual(product_obj.created_by, self.seller)

    def test_product_update_by_unauthenticated_user(self):
        """
            Test editing the product by unauthenticated user using PATCH and PUT requests.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.seller_token.key)
        # create a new product
        product_dict = {
            "category": 1,
            "title": "Asus TUF",
            "slug": 'asus_tuf',
            "description": '8GB RAM 15.6" FHD display',
            "price": 12000.00,
        }
        resp = self.client.post("/api/v1/products/", product_dict)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Product.objects.all().count(), 3)
        product_slug = resp.json()["slug"]

        # remove the credentials
        self.client.credentials()

        # Update the product with PATCH request
        product_patch = {"title": "Test change", "description": "description change"}
        resp = self.client.patch(f"/api/v1/products/{product_slug}/",
                                 json.dumps(product_patch),
                                 content_type='application/json'
                                 )
        self.assertEqual(resp.status_code, 401)

        # Check if the data changed after update the product with PUT request
        product = Product.objects.get(slug=product_dict['slug'])
        resp = self.client.get(f"/api/v1/products/{product_slug}/")
        product_resp = resp.json()
        self.assertEqual(product_resp['title'], product_dict['title'])
        self.assertEqual(product_resp['description'], product_dict['description'])
        # Update the product with PUT request
        product_resp['price'] = 5000
        product_resp['title'] = "Asus Tuf A15"

        resp = self.client.put(f"/api/v1/products/{product_slug}/",
                               json.dumps(product_resp),
                               content_type="application/json"
                               )
        self.assertEqual(resp.status_code, 401)

        resp = self.client.get(f"/api/v1/products/{product_slug}/")
        product_resp = resp.json()
        self.assertEqual(product_dict['price'], float(product_resp['price']))
        self.assertEqual(product_dict['title'], product_resp['title'])

    def test_create_review_for_product_by_authenticated_user(self):
        """
        test creating a review for the product by authenticated user
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)
        created_product = self.create_product_and_review_for_test()
        product = created_product['product']
        product_patch = created_product['product_patch']
        review = created_product['review']
        resp = self.client.patch(f"/api/v1/products/{product.slug}/",
                                 json.dumps(product_patch),
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        reviews = resp.json()['reviews']
        self.assertEqual(review['rate'], int(reviews[0]['rate']))
        self.assertEqual(review['content'], reviews[0]['content'])

    def test_create_review_for_product_by_unauthenticated_user(self):
        """
        test creating a review for the product by unauthenticated user
        """
        self.client.credentials()
        created_product = self.create_product_and_review_for_test()
        product = created_product['product']
        product_patch = created_product['product_patch']

        resp = self.client.patch(f"/api/v1/products/{product.slug}/",
                                 json.dumps(product_patch),
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 401)
        reviews = product.reviews.count()
        self.assertTrue(reviews == 0)

    def test_product_list_with_empty_search(self):
        """
        Test that search with empty string returns all products
        """
        resp = self.client.get("/api/v1/products/?search=")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)

    def test_product_list_with_whitespace_search(self):
        """
        Test that search with whitespace is trimmed and ignored
        """
        resp = self.client.get("/api/v1/products/?search=   ")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)

    def test_product_list_with_matching_search(self):
        """
        Test that search with matching query returns results
        """
        resp = self.client.get("/api/v1/products/?search=T-shirt")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "T-shirt")

    def test_product_list_with_no_matching_search(self):
        """
        Test that search with no matches returns empty results with proper structure
        """
        resp = self.client.get("/api/v1/products/?search=nonexistent")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 0)
        self.assertIn("results", data)
        self.assertEqual(data["results"], [])

    def test_category_retrieve_with_products(self):
        """
        Test category retrieve returns products properly
        """
        resp = self.client.get("/api/v1/categories/clothes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("category", data)
        self.assertIn("products", data)
        self.assertIn("count", data["products"])
        self.assertIn("results", data["products"])
        self.assertIn("is_empty", data["products"])

    def test_category_retrieve_with_no_products(self):
        """
        Test category retrieve when no active products exist
        """
        resp = self.client.get("/api/v1/categories/laptops/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("category", data)
        self.assertIn("products", data)
        self.assertIn("is_empty", data["products"])

    def test_product_retrieve_returns_product(self):
        """
        Test that individual product can be retrieved
        """
        resp = self.client.get("/api/v1/products/t-shirt/")
        self.assertEqual(resp.status_code, 200)

    def test_product_list_empty_results_structure(self):
        """
        Test that product list always returns proper structure even when empty
        """
        resp = self.client.get("/api/v1/products/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)

    def test_category_faceted_filtering_price_range(self):
        """
        Test faceted filtering by min_price and max_price on category retrieve
        """
        resp = self.client.get("/api/v1/categories/clothes/?min_price=100&max_price=150")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["products"]["count"], 1)
        self.assertEqual(data["products"]["results"][0]["title"], "T-shirt")

        resp_none = self.client.get("/api/v1/categories/clothes/?min_price=200")
        self.assertEqual(resp_none.status_code, 200)
        data_none = resp_none.json()
        self.assertEqual(data_none["products"]["count"], 0)
        self.assertTrue(data_none["products"]["is_empty"])

    def test_category_faceted_filtering_in_stock(self):
        """
        Test faceted filtering by in_stock on category retrieve
        """
        resp = self.client.get("/api/v1/categories/clothes/?in_stock=true")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["products"]["count"], 1)

        resp_out = self.client.get("/api/v1/categories/clothes/?in_stock=false")
        self.assertEqual(resp_out.status_code, 200)
        data_out = resp_out.json()
        self.assertEqual(data_out["products"]["count"], 0)

    def test_category_facets_in_response(self):
        """
        Test category retrieve includes facet statistics in response
        """
        resp = self.client.get("/api/v1/categories/clothes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("facets", data)
        facets = data["facets"]
        self.assertIn("price_range", facets)
        self.assertIn("in_stock_count", facets)
        self.assertIn("out_of_stock_count", facets)
        self.assertIn("total_count", facets)
        self.assertEqual(facets["total_count"], 1)
        self.assertEqual(facets["in_stock_count"], 1)
        self.assertEqual(facets["price_range"]["min"], 125.25)
        self.assertEqual(facets["price_range"]["max"], 125.25)

    def test_category_facets_dedicated_endpoint(self):
        """
        Test dedicated /api/v1/categories/<slug>/facets/ endpoint
        """
        resp = self.client.get("/api/v1/categories/clothes/facets/")
        self.assertEqual(resp.status_code, 200)
        facets = resp.json()
        self.assertIn("price_range", facets)
        self.assertIn("in_stock_count", facets)
        self.assertEqual(facets["total_count"], 1)

    def test_product_faceted_filtering_by_category(self):
        """
        Test filtering catalog products by category slug and id
        """
        resp = self.client.get("/api/v1/products/?category=clothes")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "T-shirt")

        resp_id = self.client.get("/api/v1/products/?category_slug=laptops")
        self.assertEqual(resp_id.status_code, 200)
        data_id = resp_id.json()
        self.assertEqual(data_id["count"], 1)
        self.assertEqual(data_id["results"][0]["title"], "Asus TUF F-15")

    def test_product_faceted_filtering_by_price_range(self):
        """
        Test filtering catalog products by price range
        """
        resp = self.client.get("/api/v1/products/?min_price=1000")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Asus TUF F-15")

        resp_low = self.client.get("/api/v1/products/?max_price=500")
        self.assertEqual(resp_low.status_code, 200)
        data_low = resp_low.json()
        self.assertEqual(data_low["count"], 1)
        self.assertEqual(data_low["results"][0]["title"], "T-shirt")

    def test_product_faceted_filtering_by_stock(self):
        """
        Test filtering catalog products by stock availability
        """
        resp = self.client.get("/api/v1/products/?in_stock=true")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

        resp_out = self.client.get("/api/v1/products/?in_stock=false")
        self.assertEqual(resp_out.status_code, 200)
        self.assertEqual(resp_out.json()["count"], 0)

    def test_product_catalog_ordering(self):
        """
        Test catalog ordering by price and title
        """
        resp_asc = self.client.get("/api/v1/products/?ordering=price")
        self.assertEqual(resp_asc.status_code, 200)
        results_asc = resp_asc.json()["results"]
        self.assertEqual(results_asc[0]["title"], "T-shirt")
        self.assertEqual(results_asc[1]["title"], "Asus TUF F-15")

        resp_desc = self.client.get("/api/v1/products/?ordering=-price")
        self.assertEqual(resp_desc.status_code, 200)
        results_desc = resp_desc.json()["results"]
        self.assertEqual(results_desc[0]["title"], "Asus TUF F-15")
        self.assertEqual(results_desc[1]["title"], "T-shirt")

        resp_title = self.client.get("/api/v1/products/?ordering=title")
        self.assertEqual(resp_title.status_code, 200)
        results_title = resp_title.json()["results"]
        self.assertEqual(results_title[0]["title"], "Asus TUF F-15")
        self.assertEqual(results_title[1]["title"], "T-shirt")

    def test_product_multi_term_catalog_search(self):
        """
        Test multi-keyword search across title and description
        """
        resp = self.client.get("/api/v1/products/?search=asus%20FHD")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "Asus TUF F-15")

    def test_product_facets_in_list_and_dedicated_endpoint(self):
        """
        Test facets in product list response and dedicated /api/v1/products/facets/
        """
        resp_list = self.client.get("/api/v1/products/")
        self.assertEqual(resp_list.status_code, 200)
        data_list = resp_list.json()
        self.assertIn("facets", data_list)
        self.assertIn("price_range", data_list["facets"])
        self.assertIn("categories", data_list["facets"])
        self.assertEqual(len(data_list["facets"]["categories"]), 2)

        resp_facets = self.client.get("/api/v1/products/facets/")
        self.assertEqual(resp_facets.status_code, 200)
        data_facets = resp_facets.json()
        self.assertIn("price_range", data_facets)
        self.assertIn("categories", data_facets)
        self.assertEqual(data_facets["total_count"], 2)
