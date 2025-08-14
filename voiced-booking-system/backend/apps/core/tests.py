from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.core.factories import UserFactory, BusinessFactory

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.business = BusinessFactory(owner=self.user)


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.business = BusinessFactory(owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def _get_headers(self):
        return {'HTTP_X_BUSINESS_ID': str(self.business.id)}
    
    def get(self, url, data=None):
        return self.client.get(url, data, **self._get_headers())
    
    def post(self, url, data=None):
        return self.client.post(url, data, format='json', **self._get_headers())
    
    def put(self, url, data=None):
        return self.client.put(url, data, format='json', **self._get_headers())
    
    def patch(self, url, data=None):
        return self.client.patch(url, data, format='json', **self._get_headers())
    
    def delete(self, url):
        return self.client.delete(url, **self._get_headers())


class CRUDTestMixin:
    model = None
    factory = None
    list_url = None
    detail_url_pattern = None
    create_data = None
    update_data = None
    
    def test_list(self):
        obj = self.factory(business=self.business)
        response = self.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create(self):
        response = self.post(self.list_url, self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.model.objects.filter(business=self.business).exists())
    
    def test_retrieve(self):
        obj = self.factory(business=self.business)
        url = self.detail_url_pattern.format(pk=obj.pk)
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(obj.id))
    
    def test_update(self):
        obj = self.factory(business=self.business)
        url = self.detail_url_pattern.format(pk=obj.pk)
        response = self.put(url, self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete(self):
        obj = self.factory(business=self.business)
        url = self.detail_url_pattern.format(pk=obj.pk)
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
