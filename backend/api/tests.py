from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationTests(APITestCase):

    def test_create_user_success(self):
        """Тест на создание нового пользователя"""
        url = reverse('foodgram_api:user-list')
        data = {
            'username': 'oxid322',
            'email': 'test@r.ru',
            'first_name': 'Все верно заполнено',
            'last_name': 'Все верно',
            'password': 'Za43@1w2e3',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'oxid322')

    def test_create_user_no_username(self):
        """Тест на создание пользователя без логина"""
        data = {
            'username': '',
            'email': 'test@r.ru',
            'first_name': 'нет логина',
            'last_name': 'нет его',
            'password': '1234',
        }
        url = reverse('foodgram_api:user-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


class UserAvatarTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword123',
                                             email='test@r.ru')
        self.client.force_authenticate(user=self.user)

    def put_avatar(self):
        url = reverse('foodgram_api:avatar')
        data = {
            "avatar": "data:image/png;base64,"
                      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///"
                      "9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByx"
                      "OyYQAAAABJRU5ErkJggg=="
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def put_invalid_avatar(self):
        url = reverse('foodgram_api:avatar')
        data = {
            "avatar": "d:i"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
