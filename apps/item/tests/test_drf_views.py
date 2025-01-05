# import pytest
# from rest_framework.test import APIRequestFactory

# from userproject.users.api.views import UserViewSet
# from userproject.users.models import User


# class TestUserViewSet:
#     @pytest.fixture
#     def api_rf(self) -> APIRequestFactory:
#         return APIRequestFactory()

#     def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
#         view = UserViewSet()
#         request = api_rf.get("/fake-url/")
#         request.user = user

#         view.request = request

#         assert user in view.get_queryset()

#     def test_me(self, user: User, api_rf: APIRequestFactory):
#         view = UserViewSet()
#         request = api_rf.get("/fake-url/")
#         request.user = user

#         view.request = request

#         response = view.me(request)  # type: ignore

#         assert response.data == {
#             "username": user.username,
#             "url": f"http://testserver/api/users/{user.username}/",
#             "name": user.name,
#         }

import json
from rest_framework.test import APITestCase
from rest_framework import status
from apps.user_account.models import User  # Import the custom User model
# from django.contrib.auth.models import User
from apps.item.models import (
    Brand, ItemGroup, ItemMaster, ItemGroupMapping, ItemVariant, ItemAttribute, 
    ItemAttributeValue, InventoryBalance, ItemInventory, TaxClassification, TaxItem, 
    ItemClassificationTaxMapping, Supplier, SupplierContact
)

class BaseViewSetTest(APITestCase):
    """
    A base test class to provide reusable setup and utility methods for viewset testing.
    """
    def setUp(self):
        """
        Set up a test user and authenticate it for testing protected endpoints.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_list_view(self, url):
        """
        Utility method to test the listing of items in a viewset.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)  # Ensure the response is a list of items

    def test_search(self, url, search_param, expected_results):
        """
        Utility method to test search functionality in a viewset.
        """
        response = self.client.get(f"{url}?search={search_param}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), expected_results)  # Match the expected number of results


class TestBrandViewSet(BaseViewSetTest):
    """
    Test cases for the BrandViewSet.
    """
    def setUp(self):
        super().setUp()
        # Creating mock data for testing
        Brand.objects.create(name="TestBrand")
        Brand.objects.create(name="AnotherBrand")

    def test_list_brands(self):
        """
        Test retrieving a list of brands.
        """
        self.test_list_view('/api/v1/brands/')

    def test_search_brand(self):
        """
        Test searching for brands by name.
        """
        self.test_search('/api/v1/brands/', 'Test', 1)


class TestItemGroupViewSet(BaseViewSetTest):
    """
    Test cases for the ItemGroupViewSet.
    """
    def setUp(self):
        super().setUp()
        # Creating mock data for testing
        ItemGroup.objects.create(group_name="Electronics")
        ItemGroup.objects.create(group_name="Furniture")

    def test_list_item_groups(self):
        """
        Test retrieving a list of item groups.
        """
        self.test_list_view('/api/v1/item-groups/')

    def test_search_item_group(self):
        """
        Test searching for item groups by group_name.
        """
        self.test_search('/api/v1/item-groups/', 'Furniture', 1)


class TestItemMasterViewSet(BaseViewSetTest):
    """
    Test cases for the ItemMasterViewSet.
    """
    def setUp(self):
        super().setUp()
        # Creating mock data for testing
        ItemMaster.objects.create(item_name="Laptop", item_code="ITM001")
        ItemMaster.objects.create(item_name="Phone", item_code="ITM002")

    def test_list_item_masters(self):
        """
        Test retrieving a list of item masters.
        """
        self.test_list_view('/api/v1/item-masters/')

    def test_search_item_master(self):
        """
        Test searching for item masters by item_name or item_code.
        """
        self.test_search('/api/v1/item-masters/', 'Laptop', 1)


class TestSupplierViewSet(BaseViewSetTest):
    """
    Test cases for the SupplierViewSet.
    """
    def setUp(self):
        super().setUp()
        # Creating mock data for testing
        Supplier.objects.create(supplier_name="SupplierA", supplier_code="SUP001")
        Supplier.objects.create(supplier_name="SupplierB", supplier_code="SUP002")

    def test_list_suppliers(self):
        """
        Test retrieving a list of suppliers.
        """
        self.test_list_view('/api/v1/suppliers/')

    def test_search_supplier(self):
        """
        Test searching for suppliers by name or code.
        """
        self.test_search('/api/v1/suppliers/', 'SupplierA', 1)
