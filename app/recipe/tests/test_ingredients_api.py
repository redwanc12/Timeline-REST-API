from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredients-list')


class PublicingredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Tests that login is required for retrieving ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateingredientsApiTests(TestCase):
    """Tests the private user ingredients API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Tests retrieving ingredients"""
        Ingredients.objects.create(user=self.user, name='Kale')
        Ingredients.objects.create(user=self.user, name='Milk')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'testpass'
        )
        Ingredients.objects.create(user=user2, name='banana')
        ingredient = Ingredients.objects.create(user=self.user, name='nuts')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""
        payload = {
            'name': "Test ingredient"
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredients.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating a new ingredient with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
